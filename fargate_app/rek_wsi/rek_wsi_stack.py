from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_ssm as ssm,
)

from aws_cdk import SecretValue


class RekWsiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #
        # ECS cluster
        #
        streamlit_task_role = iam.Role(
            self, 'StreamlitTaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            description='ECS Task Role assumed by the Streamlit task deployed to ECS+Fargate',
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, 'RekognitionReadOnlyPolicy',
                    managed_policy_arn='arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess'
                ),
            ],
        )

        ecs_container_image = ecs.ContainerImage.from_ecr_repository(
            repository=ecr.Repository.from_repository_name(
                self,
                'ECRRepo',
                ssm.StringParameter.value_from_lookup(self, '/rek_wsi/prod/ecr_repo_name')
            ),
            tag='latest'
        )

        vpc = ec2.Vpc(self, 'RekWSI', max_azs=3)
        cluster = ecs.Cluster(self, 'RekWSICluster', vpc=vpc)
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, 'RekWSIECSApp',
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs_container_image,
                container_port=8501,
                task_role=streamlit_task_role,
            ),
            public_load_balancer=True,
        )

        # CI/CD pipeline
        pipeline = codepipeline.Pipeline(self, 'RekWSIPipeline')

        #
        # Source stage
        #

        # Create an artifact that points at the code pulled from GitHub.
        source_output = codepipeline.Artifact()

        # Create a source stage that pulls the code from GitHub. The repo parameters are
        # stored in SSM, and the OAuth token in Secrets Manager.
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name='GitHub',
            output=source_output,
            oauth_token=SecretValue.secrets_manager(
                ssm.StringParameter.value_from_lookup(self, '/rek_wsi/prod/github/token'),
                json_field='oauthToken'),
            trigger=codepipeline_actions.GitHubTrigger.WEBHOOK,
            owner=ssm.StringParameter.value_from_lookup(self, '/rek_wsi/prod/github/owner'),
            repo=ssm.StringParameter.value_from_lookup(self, '/rek_wsi/prod/github/repo'),
            branch=ssm.StringParameter.value_from_lookup(self, '/rek_wsi/prod/github/branch'),
        )

        # Add the source stage to the pipeline.
        pipeline.add_stage(
            stage_name='GitHub',
            actions=[source_action]
        )

        #
        # Build stage
        #

        # Create an IAM role that grants CodeBuild access to Amazon ECR to push containers.
        build_role = iam.Role(self, 'RekWsiCodeBuildAccessRole',
                              assumed_by=iam.ServicePrincipal('codebuild.amazonaws.com'))

        # Permissions are granted through an AWS managed policy, AmazonEC2ContainerRegistryFullAccess.
        managed_ecr_policy = iam.ManagedPolicy.from_managed_policy_arn(
            self, 'cb_ecr_policy',
            managed_policy_arn='arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess',
        )
        build_role.add_managed_policy(policy=managed_ecr_policy)

        # Create a CodeBuild project that logs into Amazon ECR, build the Docker container,
        # and pushes it into the corresponding ECR repository. The project also creates an
        # imagedefinitions.json file to be used for the deployment.
        #
        # The build project needs to know the image repository name and the image tag to use,
        # as well as the AWS account ID; we use environment variables to pass these to the job.
        container_name = fargate_service.task_definition.default_container.container_name
        build_project = codebuild.PipelineProject(
            self,
            'RekWSIProject',
            build_spec=codebuild.BuildSpec.from_object({
                'version': '0.2',
                'phases': {
                    'pre_build': {
                        'commands': [
                            'env',
                            'COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)',
                            'export TAG=${COMMIT_HASH:=latest}',
                            'aws ecr get-login-password --region $AWS_DEFAULT_REGION | '
                            'docker login --username AWS '
                            '--password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
                        ]
                    },
                    'build': {
                        'commands': [
                            # Build the Docker image
                            'cd fargate_app/streamlit_app && docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .',
                            # Tag the image
                            'docker tag $IMAGE_REPO_NAME:$IMAGE_TAG '
                            '$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG',
                        ]
                    },
                    'post_build': {
                        'commands': [
                            # Push the container into ECR.
                            'docker push '
                            '$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG',
                            # Generate imagedefinitions.json
                            'cd ..',
                            "printf '[{\"name\":\"%s\",\"imageUri\":\"%s\"}]' "
                            f"{container_name} "
                            "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG "
                            "> imagedefinitions.json",
                            'ls -l',
                            'pwd',
                            'sed -i s"|REGION_NAME|$AWS_DEFAULT_REGION|g" appspec.yaml',
                            'sed -i s"|ACCOUNT_ID|$AWS_ACCOUNT_ID|g" appspec.yaml',
                            'sed -i s"|TASK_NAME|$IMAGE_REPO_NAME|g" appspec.yaml',
                            # f'sed -i s"|CONTAINER_NAME|{ecs_container_image.image_name}|g" appspec.yaml',
                            f'sed -i s"|CONTAINER_NAME|{container_name}|g" appspec.yaml',
                            'echo ">>> appspec.yaml ---"',
                            'cat appspec.yaml',
                            'echo "<<< ----------------"',
                            'echo ">>> imagedefinitions.json ---"',
                            'cat imagedefinitions.json',
                            'echo "<<< ----------------"',
                        ]
                    }
                },
                'artifacts': {
                    'files': [
                        'imagedefinitions.json',
                        'appspec.yaml',
                    ],
                },
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            environment_variables={
                'AWS_ACCOUNT_ID':
                    codebuild.BuildEnvironmentVariable(value=self.account),
                'IMAGE_REPO_NAME':
                    codebuild.BuildEnvironmentVariable(
                        value=ssm.StringParameter.value_from_lookup(self, '/rek_wsi/prod/ecr_repo_name')),
                'IMAGE_TAG':
                    codebuild.BuildEnvironmentVariable(value='latest'),
            },
            role=build_role,
        )

        # Create an artifact to store the build output.
        build_output = codepipeline.Artifact()

        # Create a build action that ties the build project, the source artifact from the
        # previous stage, and the output artifact together.
        build_action = codepipeline_actions.CodeBuildAction(
            action_name='Build',
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        # Add the build stage to the pipeline.
        pipeline.add_stage(
            stage_name='Build',
            actions=[build_action]
        )

        deploy_action = codepipeline_actions.EcsDeployAction(
            action_name='Deploy',
            service=fargate_service.service,
            # image_file=build_output
            input=build_output,
        )

        pipeline.add_stage(
            stage_name='Deploy',
            actions=[deploy_action],
        )
