check-init:
	cdk synth -c stage=dev env-dev

deploy-init:
	cdk synth -c stage=dev env-dev

deploy-all:
	cdk synth -c stage=dev env-dev
	cdk synth -c stage=dev ecr-dev

clean:
	rm -rf cdk.out __pycache__ cdk.context.json
