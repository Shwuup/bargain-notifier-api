kill:
	fuser -k 3000/tcp

deploy-local:
	sam build -t ./template.yaml
	sam local start-api

deploy-dev:
	sam build -t ./template.yaml
	sam deploy --parameter-overrides "ParameterKey=Stage,ParameterValue=dev ParameterKey=UserTable,ParameterValue=Users-dev ParameterKey=LatestUrlTable,ParameterValue=LatestUrl-dev ParameterKey=SeenDealsTable,ParameterValue=SeenDeals-dev" --config-file samconfig_dev.toml

deploy-prod:
	sam build -t ./template.yaml
	sam deploy --parameter-overrides "ParameterKey=Stage,ParameterValue=prod ParameterKey=UserTable,ParameterValue=Users-prod ParameterKey=LatestUrlTable,ParameterValue=LatestUrl-prod ParameterKey=SeenDealsTable,ParameterValue=SeenDeals-dev" --config-file samconfig_prod.toml
