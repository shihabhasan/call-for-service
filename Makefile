.PHONY: deploy

deploy:
	ansible-playbook -i deployment/inventory/production --ask-vault-pass  -t deploy deployment/playbook/all.yml 

provision:
	ansible-playbook -i deployment/inventory/production --ask-vault-pass deployment/playbook/all.yml 	