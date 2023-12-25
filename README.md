# Dokumentacja dla Kodu Serwera i Klienta

Ten dokument opisuje, jak uruchomić serwer i klienta do odczytywania danych z tabel.

## Wymagania

Upewnij się, że masz zainstalowane następujące biblioteki:

- pyarrow
- pandas

Możesz je zainstalować za pomocą pip:

```bash
pip install pyarrow pandas
```

## Uruchomienie serwera

Przejdź do odpowiedniego katalogu:

```bash
cd client-server-code
```

Uruchom skrypt serwera:

```bash
py server.py
```

Serwer teraz powinien działać i oczekiwać na połączenia od klienta.

## Uruchomienie Klienta

W tym samym katalogu uruchom skrypt klienta, aby odczytać dane z tabel:

```bash
py client.py
```
