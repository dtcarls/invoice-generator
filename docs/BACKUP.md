# Invoice Generator — Backup & Restore

All application data — the SQLite database and all generated PDFs — lives in the `./data/` directory on your host machine.

---

## Backup

### 1. Stop the Container

```bash
docker compose down
```

### 2. Copy the Data Directory

```bash
cp -r ./data ./data-backup-$(date +%Y%m%d)
```

Or use `tar` to create a compressed archive:

```bash
tar -czf invoice-backup-$(date +%Y%m%d).tar.gz ./data
```

The backup contains:
- `data/invoices.db` — the SQLite database (all invoices, clients, settings)
- `data/pdfs/` — generated invoice PDF files
- `data/receipts/` — generated receipt PDF files
- `data/logos/` — uploaded business logo files

### 3. Restart the Application

```bash
docker compose up -d
```

---

## Restore

### 1. Stop the Container

```bash
docker compose down
```

### 2. Replace the Data Directory

```bash
rm -rf ./data
cp -r ./data-backup-20240101 ./data
```

Or from a tar archive:

```bash
rm -rf ./data
tar -xzf invoice-backup-20240101.tar.gz
```

### 3. Start the Application

```bash
docker compose up -d
```

All invoices, clients, settings, and PDFs will be restored exactly as they were.

---

## Notes

- **No migration needed**: The database schema is created automatically on startup using `CREATE TABLE IF NOT EXISTS`. Restoring from a backup of the same application version requires no additional steps.
- **Scheduled backups**: You can automate backups with a cron job. Make sure to stop the container first (or use SQLite's `.backup` command) to avoid a corrupt database file during a write.
- **Disk space**: PDFs are retained indefinitely. Review and archive old PDFs periodically if disk space is a concern.
