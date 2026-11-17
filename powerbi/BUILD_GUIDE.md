# Power BI dashboard instructions

A `.pbix` file requires Power BI Desktop, which is not available in this build environment. This folder contains **working DAX measure definitions** and a reproducible dashboard recipe, not a prebuilt `.pbix`.

1. Open Power BI Desktop > Get Data > Text/CSV > `data/transactions.csv`.
2. In Power Query, set `order_date` to Date, `customer_id`, `product_id`, `quantity`, `order_id` to Whole Number, and numeric amounts to Decimal Number. Apply changes.
3. Rename the imported table to `Transactions`.
4. Create each measure in `MEASURES.dax` individually using Modeling > New measure. Do not paste the whole file as a single measure.
5. Page 1 Executive: cards Revenue, Product Profit, Profit Margin %, Completed Orders; line chart Revenue by order_date (month); bar chart Product Profit by category; region slicer.
6. Page 2 Customers: cards Unique Customers, Return Rate %; stacked bars by region and category; monthly order trend.
7. Page 3 Profitability: matrix category × region with Revenue, Product Cost, Product Profit, Profit Margin %; product-level drill-through on product_id.
8. Format monetary values as currency and percentage measures as percentages.
9. Document the assumption: revenue/profit exclude returned and cancelled orders; cost is product cost only, not full operating cost.

For RFM and cohort visuals, export the analysis from Python or connect to the provided PostgreSQL queries.
