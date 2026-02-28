# Auction Service

## Run

```bash
git clone https://github.com/VladSkopenko/UD_test_task.git
cd UD_test_task
docker compose up --build
```

App: **http://localhost:8000**

---

## API

### Create lot

```bash
curl -X POST http://localhost:8000/api/v1/lots \
  -H "Content-Type: application/json" \
  -d '{"title": "iPhone 15 Pro", "starting_price": 999.99}'
```

### List active lots

```bash
curl http://localhost:8000/api/v1/lots
```

### Place bid

```bash
curl -X POST http://localhost:8000/api/v1/lots/1/bids \
  -H "Content-Type: application/json" \
  -d '{"bidder_name": "Alice", "amount": 1100.00}'
```

Swagger UI: **http://localhost:8000/docs**


---

## WebSocket

```bash
# install wscat
npm install -g wscat

# connect to lot #1
wscat -c ws://localhost:8000/api/v1/ws/lots/1
```

Then place a bid — events will arrive in the terminal:

```json
{"type": "new_bid", "amount": "1100.00", "bidder_name": "Alice", "created_at": "..."}
{"type": "time_extended", "end_time": "..."}
{"type": "lot_ended", "status": "ended"}
```

---

## Frontend

Open **http://localhost:8000** — create lots, place bids, watch live events.

---

## Config (`public_env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUCTION_LOT_DURATION_MINUTES` | `5` | Lot duration in minutes |
| `AUCTION_EXTEND_MINUTES` | `1` | Time extension per bid |
| `AUCTION_CLOSE_LOTS_INTERVAL_SEC` | `30` | Background task interval |
