class MyImporter(MyXLSXImporterModel):
    class Meta:
        config_file = 'import_test.json'
        model = Prices
        delimiter = ','
