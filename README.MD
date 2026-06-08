# StockPulse


## English

### What it is
StockPulse is a desktop application in Python for inventory management, sales tracking, and demand forecasting. The app is built without a direct SQL database connection: it uses the schema from `d.sql` as a design reference and stores data locally in JSON.

### How it was created
- `d.sql` describes the tables and initial sample data:
  - `usuarios`
  - `fornecedores`
  - `produtos`
  - `vendas`
- Refactored architecture: the code separates business logic, predictive calculations and JSON persistence from the UI (the app uses a controller-style `StockController` to keep logic decoupled from `tkinter`).
- The Python app initializes sample data if `stockpulse_data.json` does not exist.
- The UI is implemented with `tkinter` to provide a desktop interface.
- Data persistence is handled via a local JSON file; the app saves automatically after changes.

### What it does
- displays products with current stock, minimum stock, and supplier
- allows product creation and editing
- allows supplier registration
- registers sales and updates stock levels with real-time validation to prevent negative stock
- automatically persists data to JSON on every action (no manual "Save" button required)
- predicts when stock will run out per product
- suggests ideal sale prices
- exports inventory and forecast reports to CSV
- has product search
- shows recent sales history

### How to use
1. Open a terminal in `c:\Users\Diogo\Downloads\Stockpulse`
2. Run:
  ```bash
  python stockpulse.py
  ```
3. Use the tabs to:
  - `Produtos` / `Products`: view products and add/edit items
  - `Fornecedores` / `Suppliers`: add suppliers
  - `Vendas` / `Sales`: register sales and update stock
  - `Previsões` / `Forecast`: see stock depletion estimates and suggested prices

### Notes
- Data is saved in `stockpulse_data.json`.
- Saving happens automatically and transparently upon creating products, suppliers, or registering sales.
- If the JSON file is invalid, the app recreates default data automatically.
- No SQL connection setup is required.

---

## Português

### O que é
StockPulse é uma aplicação desktop em Python para gerenciamento de estoque, vendas e previsão de demanda. O aplicativo foi criado sem uma conexão direta com banco de dados SQL: em vez disso, ele usa o esquema do arquivo `d.sql` como base para estruturar dados e armazena tudo localmente em JSON.

### Como foi criado
- O arquivo `d.sql` define as tabelas e dados iniciais:
  - `usuarios`
  - `fornecedores`
  - `produtos`
  - `vendas`
- Arquitetura refatorada: o código separa lógica de negócio, cálculos de previsão e persistência em JSON da interface gráfica (foi adotado um padrão controlador, `StockController`, para manter lógica desacoplada do `tkinter`).
- O Python inicializa dados de exemplo se `stockpulse_data.json` não existir.
- A interface gráfica usa `tkinter` para fornecer uma aplicação desktop.
- A persistência é feita em arquivo JSON local; o app salva automaticamente após alterações.

### O que faz
- exibe produtos com quantidade atual, quantidade mínima e fornecedor
- permite cadastro/edição de produtos
- permite cadastro de fornecedores
- registra vendas e atualiza o estoque com validação em tempo real para evitar estoque negativo
- persiste automaticamente os dados em JSON a cada ação (não é necessário botão "Salvar")
- prevê quando o estoque irá acabar por produto
- sugere preço ideal de venda
- exporta relatórios CSV de estoque e previsão
- oferece busca por produtos
- mostra histórico de vendas recente

### Como usar
1. Abra um terminal em `c:\Users\Diogo\Downloads\Stockpulse`
2. Execute:
  ```bash
  python stockpulse.py
  ```
3. Use as abas para:
  - `Produtos`: ver produtos e adicionar/editar itens
  - `Fornecedores`: cadastrar fornecedores
  - `Vendas`: registrar vendas e atualizar estoque
  - `Previsões`: verificar estimativas de esgotamento e preços sugeridos

### Observações
- Os dados são salvos em `stockpulse_data.json`.
- O salvamento ocorre automaticamente e de forma transparente ao criar produtos, fornecedores ou registrar vendas.
- Se o arquivo JSON estiver inválido, o app recria os dados padrão automaticamente.
- Não é necessário configurar conexão SQL.