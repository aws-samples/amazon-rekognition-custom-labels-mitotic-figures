#!/usr/bin/env python3
from aws_cdk import App, Environment
from rek_wsi.rek_wsi_stack import RekWsiStack


app = App()
# env = core.Environment(account='<YOUR_AWS_ACCOUNT_ID>', region='<YOUR_AWS_REGION>')
env = Environment(account='038821543405', region='eu-west-1')
RekWsiStack(app, "RekWsiStack", env=env)

app.synth()
