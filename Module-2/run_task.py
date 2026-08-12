from tasks import process_pdf

result = process_pdf.delay("invoice.pdf")

print("Task Submitted!")
print(result.id)
