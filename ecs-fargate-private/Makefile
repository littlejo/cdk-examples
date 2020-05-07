check-init:
	cdk synth -c stage=dev env-dev

deploy-init:
	cdk deploy --require-approval never -c stage=dev env-dev

deploy-all:
	cdk deploy --require-approval never -c stage=dev env-dev
	cdk deploy --require-approval never -c stage=dev ecr-dev
	cdk deploy --require-approval never -c stage=dev ecr-2-dev

destroy-all:
	cdk destroy -c stage=dev ecr-2-dev
	cdk destroy -c stage=dev ecr-dev
	cdk destroy -c stage=dev env-dev

destroy-ecr:
	cdk destroy -c stage=dev ecr-dev

deploy-ecr:
	cdk deploy --require-approval never -c stage=dev ecr-dev

clean:
	rm -rf cdk.out __pycache__ cdk.context.json
