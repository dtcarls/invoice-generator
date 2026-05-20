# Invoice Generator — Usage Guide

A self-hosted PDF invoice generator that runs entirely in Docker with no external dependencies.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10 or later
- [Docker Compose](https://docs.docker.com/compose/) v2 or later (included with Docker Desktop)

---

## 1. Getting Started

Clone the repository and start the application:

```bash
git clone <repository-url> invoice-generator
cd invoice-generator
mkdir -p data
docker compose up --build -d
```

The app will be available at **http://localhost:8000**.

To view logs:

```bash
docker compose logs -f
```

To stop the application:

```bash
docker compose down
```

---

## 2. First-Time Setup: Business Settings

Before creating invoices, fill in your business information.

1. Open http://localhost:8000/settings
2. Fill in your business name, address, email, phone, and tax ID
3. Optionally upload a logo (PNG or JPEG, displayed on all PDFs)
4. Set your default currency (e.g. `USD`, `EUR`, `GBP`)
5. Set default due days (e.g. `30` for Net-30 terms)
6. Add default payment instructions (e.g. bank account details)
7. Click **Save Settings**

---

## 3. Adding Clients

Each invoice is linked to a client record.

1. Go to http://localhost:8000/clients
2. Click **+ New Client**
3. Enter the client's name, contact name, address, and email
4. Click **Save Client**

Clients can be edited or archived at any time. Archived clients are hidden from the new-invoice form but remain linked to existing invoices.

---

## 4. Creating an Invoice

1. Go to http://localhost:8000/invoices or click **+ New Invoice** on the dashboard
2. Select a client from the dropdown
3. Set the issue date and due date
4. Choose the currency for this invoice
5. Add one or more line items (description, quantity, unit price)
   - Click **+ Add Item** to add more rows
   - Remove a row with the **×** button
6. Optionally add notes or override the payment instructions for this invoice
7. Click **Create Invoice**

A PDF is generated immediately and stored on disk. You are redirected to the invoice detail page.

---

## 5. Downloading the Invoice PDF

On the invoice detail page, click **Download Invoice PDF** to download the generated PDF.

You can also access it directly at:

```
http://localhost:8000/invoices/{id}/pdf
```

---

## 6. Marking an Invoice as Paid

When a client pays, record the payment to auto-generate a receipt PDF.

1. Open the invoice detail page
2. Click **Mark as Paid** (expand the section)
3. Enter the payment date
4. Enter the payment method (e.g. `Bank transfer`, `Check #1234`, `PayPal`)
5. Click **Confirm Payment**

A receipt PDF is generated automatically with a sequential receipt number (`RCT-YYYY-MM-DD-NNNN`).

---

## 7. Downloading the Receipt PDF

After marking an invoice as paid, a **Download Receipt PDF** button appears on the invoice detail page.

Direct URL:

```
http://localhost:8000/invoices/{id}/receipt.pdf
```

---

## 8. Marking an Invoice as Unpaid

To reverse a payment (e.g. a bounced check):

1. Open the invoice detail page
2. Click **Mark Unpaid**

This clears the payment date, receipt number, and deletes the receipt PDF from disk. The invoice PDF is not affected.

---

## 9. Service Presets

Frequently used line items can be saved as service presets to speed up invoice creation.

1. Go to http://localhost:8000/services
2. Click **+ New Service**
3. Enter a description and default unit price
4. Click **Save**

Presets appear as a dropdown on the new invoice form — selecting one fills in the description and price for a line item.

---

## Data Persistence

All data (database and PDFs) is stored in the `./data/` directory on your host machine, mounted into the container. Data persists across container restarts and upgrades.

See [BACKUP.md](BACKUP.md) for backup instructions.
