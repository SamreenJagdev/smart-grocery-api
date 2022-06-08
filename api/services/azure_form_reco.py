from datetime import datetime
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from api.schemas.receipt import ReceiptSchema
from api.services.utils import Utils

endpoint = "https://4fd3-scan.cognitiveservices.azure.com/"
key = "ea7bfa6f6eb9498cb0c6093f24421283"


class AzureFormReco:

    def analyze_document(file_input):

        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-receipt", file_input
        )
        receipts = poller.result()
        temp_receipt = {}

        temp_receipt["name"] = "temp-name"

        for idx, receipt in enumerate(receipts.documents):

            if receipt.fields.get("MerchantName"):
                temp_receipt["merchant_name"] = receipt.fields.get("MerchantName").value
            else:
                temp_receipt["merchant_name"] = "Unknown Store"

            receipt_date = receipt.fields.get("TransactionDate").value if receipt.fields.get("TransactionDate") is not None else None
            receipt_time = receipt.fields.get("TransactionTime").value if receipt.fields.get("TransactionTime") is not None else None
            temp_date = Utils.get_timestamp(receipt_date, receipt_time)
            if temp_date is not None:
                temp_receipt["creation_timestamp"] = temp_date

            scanned_items = []
            if receipt.fields.get("Items"):

                for idx, item in enumerate(receipt.fields.get("Items").value):
                    temp_item = {}

                    if item.value.get("Name"):
                        temp_item["name"] = item.value.get("Name").value
                    else:
                        temp_item["name"] = "Unknown Item"

                    if item.value.get("Quantity"):
                        temp_item["quantity"] = item.value.get("Quantity").value

                    if item.value.get("Price"):
                        temp_item["price"] = item.value.get("Price").value

                    if item.value.get("TotalPrice"):
                        temp_item["total_price"] = item.value.get("TotalPrice").value

                    scanned_items.append(temp_item)

                temp_receipt["items"] = scanned_items

        return ReceiptSchema().load(temp_receipt)
