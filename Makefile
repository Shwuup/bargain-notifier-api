build:
	sam build -t ./template.yaml

kill:
	fuser -k 3000/tcp

deploy-local:
	sam local start-api

deploy-dev:
	sam deploy --parameter-overrides "ParameterKey=Stage,ParameterValue=dev ParameterKey=UserDB,ParameterValue=Users-dev ParameterKey=LatestUrlDB,ParameterValue=LatestUrl-dev" --config-file samconfig_dev.toml

deploy-prod:
	sam deploy --parameter-overrides "ParameterKey=Stage,ParameterValue=prod ParameterKey=UserDB,ParameterValue=Users-prod ParameterKey=LatestUrlDB,ParameterValue=LatestUrl-prod" --config-file samconfig_prod.toml
