master:
	python api/app.py

gomaster:
	cd api && gin --appPort 5050 --port 3000

gorun:
	go run api/app.go
