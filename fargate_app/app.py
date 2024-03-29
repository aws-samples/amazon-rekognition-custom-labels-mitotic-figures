#!/usr/bin/env python3
from aws_cdk import App, Environment
from rek_wsi.rek_wsi_stack import RekWsiStack


app = App()
env = Environment(account='<YOUR_AWS_ACCOUNT_ID>', region='<YOUR_AWS_REGION>')
RekWsiStack(app, "RekWsiStack", env=env)

app.synth()
