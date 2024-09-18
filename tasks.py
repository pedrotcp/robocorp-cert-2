from robocorp.tasks import task
from robocorp import browser

from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive

# Global variables
http = HTTP()
library = Tables()

@task
def order_robots_from_RobotSpareBin():
    global page
    page = browser.page()
    # browser.configure(
    #     slowmo=100
    # )
    """
    Orders robots
    Saves order HTML as  PDF file
    Saves the screenshot
    Embeds screenshot
    ZIPs receipts and images
    """


    open_website()
    click_popup()
    download_csv()
    fills_form()
    archive_receipts()

def open_website():
    """Navigates to URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def click_popup():
    """Logs in and clicks the 'Log in' button"""
    page.click("button:text('OK')")

def download_csv():
    """Downloads CSV """
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fills_form():
    """Reads file and populates variable"""
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    for row in orders:

        page.select_option("#head", f"{row['Head']}")
        page.check(f"#id-body-{row['Body']}")
        page.fill(".form-control", f"{row['Legs']}")
        page.fill("#address", f"{row['Address']}")
        page.click("button:text('Preview')")
        page.click("button:text('Order')")

        while (True):
            error = page.query_selector(".alert-danger")
            if (error):
                page.wait_for_timeout(1000)
                page.click("button:text('Order')")
            else:
                break

        store_receipt(row["Order number"])
        screenshot(row["Order number"])
        embed_screenshot(f"output/{row['Order number']}.png", f"output/receipts/{row['Order number']}.pdf")

        page.click("button:text('Order another robot')")
        page.click("button:text('OK')")



def store_receipt(order_number):
    print(order_number)
    pdf = PDF()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(order_receipt_html, f"output/receipts/{order_number}.pdf")

def screenshot(order_number):
    locator = page.locator("#robot-preview-image")
    locator.screenshot(path=f"output/{order_number}.png")

def embed_screenshot(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot], pdf_file, append=True)

def archive_receipts():
    zip = Archive()
    zip.archive_folder_with_zip("./output", "./output/receipts.zip", compression="bzip2")

