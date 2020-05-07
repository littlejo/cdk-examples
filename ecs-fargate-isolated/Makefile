check-init:
	cdk synth -c stage=dev env-dev

deploy-init:
	cdk deploy -c stage=dev env-dev

deploy-all:
	cdk deploy -c stage=dev env-dev
	cdk deploy -c stage=dev ecr-dev

clean:
	rm -rf cdk.out __pycache__ cdk.context.json
