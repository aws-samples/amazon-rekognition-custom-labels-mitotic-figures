#!/usr/bin/env python3
from aws_cdk import core

from rek_wsi.rek_wsi_stack import RekWsiStack


app = core.App()
env = core.Environment(account='<YOUR_AWS_ACCOUNT_ID>', region='<YOUR_AWS_REGION>')
RekWsiStack(app, "RekWsiStack", env=env)

app.synth()
