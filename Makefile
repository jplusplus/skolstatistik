
deploy: # upload to aws s3
	aws s3 cp data/* s3://skolverket-statistik/ --recursive
