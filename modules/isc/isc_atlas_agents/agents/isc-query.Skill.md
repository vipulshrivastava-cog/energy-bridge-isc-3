---
name: isc-query
description: >-
  How to read supply chain data with the ISC Atlas Query tool: which call fits which question shape,
  how to write filters that the API accepts, how to read what comes back, and where the tool's reach
  ends. Use for one-hop reads — a named record, one view with a filter, a count, or the edges from one
  anchor. View, space and edge facts come from isc-model.
metadata:
  argument-hint: "business question + any externalId the user named"
---

# Reading with ISC Atlas Query

Atlas Query is the fast path: one request, no code. It reads **one view at a time**. A question that
needs two views joined, a whole subtree, arithmetic across rows, or a complete list is outside what it
can finish — see *Where Atlas Query's reach ends*.

Views, spaces, edge families, hierarchies and where each value lives are in **isc-model**. This skill
does not repeat them; it is about making the call and reading the result.

## Procedure

1. **Name the record.** Business noun → view and space (isc-model). If the question names a value rather
   than a record, isc-model's *Where values live* says which record carries it — often an edge.
2. **Resolve the entity.** If the user gave a business name and not an externalId, find the record first
   with `search_instances`, or `list_instances` filtered on `name`. Use only externalIds that came from
   the user or from a result; an invented or remembered id returns a confident wrong answer.
3. **Pick the call** from the question shape (table below).
4. **Project only what the answer needs** — externalId, name, status, quantity, dates, reason. Large
   results crowd out reasoning and slow the turn.
5. **Check the result against the question** before writing anything: is this the record asked about, and
   does it carry every part of the question? If a part is missing, it is somewhere else — not absent.

| Question shape | Call |
|----------------|------|
| Everything about one named record | `retrieve_instances` on its view |
| Records matching an attribute | `list_instances` with a filter on that property |
| Records linked to a named record by a direct relation | `list_instances` on the **child** view, filtering the relation (isc-model lists the links that exist only on the child) |
| The cost, quantity, status, validity or role of an M:N link | `list_instances` on the edge view, anchored on `startNode` or `endNode` |
| How many, total, highest, per group | `aggregate_instances` |
| Find a record by business name | `search_instances` |

Call a data tool in the first turn. The views and spaces are fixed in isc-model, so there is nothing to
ask the user and nothing to discover before the first read.

## Writing filters the API accepts

- **Direct relations take a reference, not a string.** The value is `{"space": <instance space>,
  "externalId": <id>}`. A bare string, or reaching into `relation.externalId`, is rejected.
- **The version carries its `v`.** `v1.0.0`. Without the leading `v` the call fails as *view not found*,
  which reads like a missing view but is a typo.
- **Edges are anchored by end.** Filter the edge view on `startNode` or `endNode` with a node reference.
  Which end your anchor is on follows from the edge's start → end direction in isc-model; the anchor at
  the far end is the other role, not a different edge type.
- **Project the properties you will cite.** A row without its `name` forces a second read.
- **Null is not reliably filterable.** List with the property projected and judge the values yourself.

## Reading the result

- A direct relation comes back as a reference, not a name. To cite it, read the target record — one
  `retrieve_instances` with every referenced id is enough for a page of rows.
- Typed hierarchy records carry no name of their own; isc-model says which base view holds it.
- Counts from `aggregate_instances` describe what the filter matched, not what exists. Say which filter
  produced the number.
- Rows come back in no meaningful order. "First", "latest" or "highest" needs an explicit sort or an
  aggregate, otherwise the first row is arbitrary.

## When a call fails or returns nothing

| What happened | What it means | What to do |
|---------------|---------------|------------|
| Filter rejected on a property the view has | That property type cannot be filtered (text lists, nulls) | List with it projected and apply the condition yourself; say so in the answer |
| *View not found* | Version without the `v`, or the view is in another domain space | Re-check against isc-model |
| Unknown property | The name was guessed | Take the name from isc-model; do not try variants |
| Edge listing rejected on this edge view | Some edge views refuse an anchor filter | Retrieve the edge by externalId if you have it; otherwise this read needs another path |
| Zero rows on a valid read | Either nothing matches, or the value lives elsewhere | Check the other place isc-model says it could live before reporting it as absent |

Repeating a rejected call unchanged produces the same rejection. Change the approach rather than the
wording.

## Where Atlas Query's reach ends

Atlas Query reads one view per call, returns a page, and does not compute. The shapes below are not
failures of a call — they are questions this tool cannot finish, whatever filter is used. Recognising
one before spending calls on it saves the turn; recognising it after a call failed stops the retry
loop.

| Signal in the question | Why Atlas Query cannot finish it |
|------------------------|----------------------------------|
| Two or more hops ("which shipments are exposed if this supplier fails") | Each hop is a separate call and the ids of hop *n+1* are only known after hop *n*; the join has to happen somewhere |
| Everything under a node, at any depth | A subtree is a prefix match on the materialized path, not a parent filter |
| "All", "every", "complete list" | A call returns a page; a partial list reported as complete is a wrong answer |
| Compare, rank, total across records, or combine two numbers that live on different records | Aggregation runs on one view; it does not join or compute across views |
| As of a date, still valid, currently active | Validity sits on edge properties that have to be compared against the date |
| A value that one read did not show | Verifying absence means looking where else it could live, which is a second shape |

Reaching the boundary is not a failed read, and reporting the question as unanswerable is not the
response to it: these shapes need a read that can join across views, page to completion, or compute.
What this tool already resolved stays useful — externalIds are the expensive part of any read, so carry
them forward rather than starting again.
