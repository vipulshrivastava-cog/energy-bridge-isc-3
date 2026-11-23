# Planning & Forecasting

> [!NOTE]
> Part of [Integrated Supply Chain](../overview.md). One of 7 core domains.

Planning & Forecasting tracks what the business expects to need, what supply has been proposed to meet it, and how limited supply is shared between customers.

## Why it matters

This is the planning layer of ISC. It takes demand signals from customers and maintenance, proposes supply through MRP (material requirements planning), and hands allocated supply to order promising in [Customer Demand Fulfilment](./customer-demand-fulfilment.md). The domain keeps three things apart: the expectation (the forecast), the proposal (the plan) and the commitment (the allocation). That separation lets you trace a customer order back to the forecast that anticipated it.

## Key concepts

| Concept | What it is |
|---|---|
| Forecast | An expected quantity of a material for a location and period: demand, consumption, production, supply or inventory. |
| Forecast version | A scenario label such as baseline, optimistic or pessimistic, so several forecasts can exist for the same material, location and period. |
| System and adjusted forecast | The model's own figure, and the planner's override of it. Keeping both makes forecast bias measurable. |
| Plan | A supply proposal from MRP to produce or buy a quantity of a material at a plant within a time window. |
| Plan adherence | How closely the actual start, finish and quantity matched what was planned. |
| Product allocation | A share of limited supply reserved for a customer or customer group over a period. |
| Headroom | What is left in an allocation after confirmed orders have used their share. |
| Allocation type | The rule for using up an allocation, such as a hard ceiling or a fair share. |
| Time bucket | The planning period a record covers: day, week, month, quarter or year. |
| Pegging | Linking supply or an allocation to the specific demand it exists to satisfy. |

## From forecast to measurement

```mermaid
flowchart LR
    A["1. Forecast demand"] --> B["2. Plan supply"] --> C["3. Allocate limited supply"] --> D["4. Consume by orders"] --> E["5. Execute and measure"]
```

1. **Forecast demand.** A forecast records the expected quantity of a material at a plant for a period. It can come from a statistical or machine-learning model, MRP, a planner, or confirmed customer orders. Planners can adjust it, and an approved version is released for planning.
2. **Plan supply.** MRP turns the forecast into a plan: a proposal to produce or buy the required quantity at a plant by a planned finish date. The forecast links to the plan it produced.
3. **Allocate limited supply.** When supply is short, an allocation reserves part of it for a customer or group for a period. It links back to the forecast it was built to meet.
4. **Consume by orders.** As customer orders are confirmed, they draw on the allocation. Each order line records which allocation it uses, along with the commercial terms of the link. The consumed and remaining quantities track the headroom.
5. **Execute and measure.** The plan becomes a production request or goes through procurement. Actual dates and quantities are recorded on the plan, and forecast accuracy is filled in once actuals are available.

## How it connects

- **[Customer Demand Fulfilment](./customer-demand-fulfilment.md)**: order lines draw on allocations, and confirmed orders can feed a forecast.
- **Manufacturing**: a plan can become a production request, and a forecast can link to the production request it supports.
- **Asset Maintenance**: maintenance work orders are a demand signal, and a plan can link to a maintenance order.
- **[Material Management](./material-management.md)**: forecasts and allocations are for a specific material at a specific location.

## Questions it helps answer

**What do we expect to need?**
- What is the forecast for this material next quarter, and which version is approved?
- How far did planners adjust the system forecast?

**What supply is proposed?**
- What has MRP proposed to meet this demand, and by when?
- How closely did the plan match what was actually produced?

**How is limited supply shared?**
- How much of this allocation is left?
- Which orders have used it, and which customers is it protected for?

## An example

A baseline forecast expects 10,000 units in September. The planner adjusts it to 11,000. MRP proposes a plan to produce 11,000 by 28 August. Supply is limited, so an allocation reserves 3,000 units for one customer group in September.

| | Quantity |
|---|---|
| Allocated | 3,000 |
| Used by confirmed orders | 2,200 |
| Headroom | 800 |

When the month ends, the plan records 10,600 units actually produced, and the forecast's accuracy is worked out from that.

## Things to know

- **Expectation, proposal and commitment are separate.** A forecast is not a promise, and a plan is not an order.
- **Both the system and the adjusted forecast are kept.** That is how forecast bias can be measured.
- **Versions coexist.** Baseline, optimistic and pessimistic forecasts can exist for the same material, location and period.
- **The allocation type decides how supply runs out.** A hard ceiling stops at the limit. A fair share spreads supply across customers.

