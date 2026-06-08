import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from tkinter import CENTER, END, Label, StringVar, Tk, ttk, messagebox, filedialog
from typing import Any, Dict, List, Optional

DATA_FILE = "stockpulse_data.json"
DEFAULT_WINDOW_DAYS = 90

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    criado_em: str

@dataclass
class Fornecedor:
    id: int
    nome_empresa: str
    contato_nome: str
    telefone: str
    email: str
    criado_em: str

@dataclass
class Produto:
    id: int
    nome: str
    descricao: str
    preco_custo: float
    preco_venda: float
    quantidade_atual: int
    quantidade_minima: int
    fornecedor_id: int
    atualizado_em: str

@dataclass
class Venda:
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: float
    data_venda: str


class StockController:
    """Classe responsável por gerenciar as regras de negócio e persistência de dados."""
    
    def __init__(self):
        self.data: Dict[str, List[Dict[str, Any]]] = self.load_data()

    def default_data(self) -> Dict[str, List[Dict[str, Any]]]:
        agora = datetime.now().isoformat(timespec="seconds")
        fornecedores = [
            Fornecedor(
                id=1,
                nome_empresa="Tech Distribuidora Ltda",
                contato_nome="Carlos Silva",
                telefone="(11) 99999-1111",
                email="carlos@techdist.com",
                criado_em=agora,
            )
        ]

        produtos = [
            Produto(
                id=1,
                nome="Teclado Mecânico RGB",
                descricao="Teclado switch azul layout ABNT2",
                preco_custo=120.00,
                preco_venda=250.00,
                quantidade_atual=45,
                quantidade_minima=15,
                fornecedor_id=1,
                atualizado_em=agora,
            ),
            Produto(
                id=2,
                nome="Mouse Gamer Pro",
                descricao="Mouse 16000 DPI sensor óptico",
                preco_custo=80.00,
                preco_venda=180.00,
                quantidade_atual=8,
                quantidade_minima=12,
                fornecedor_id=1,
                atualizado_em=agora,
            ),
        ]

        vendas = [
            Venda(id=1, produto_id=1, quantidade=5, preco_unitario=250.00, data_venda="2026-03-01 14:00:00"),
            Venda(id=2, produto_id=1, quantidade=8, preco_unitario=250.00, data_venda="2026-04-01 10:30:00"),
            Venda(id=3, produto_id=1, quantidade=12, preco_unitario=250.00, data_venda="2026-05-01 16:15:00"),
            Venda(id=4, produto_id=2, quantidade=2, preco_unitario=180.00, data_venda="2026-05-10 11:00:00"),
            Venda(id=5, produto_id=2, quantidade=4, preco_unitario=180.00, data_venda="2026-06-01 09:45:00"),
        ]

        return {
            "usuarios": [],
            "fornecedores": [asdict(f) for f in fornecedores],
            "produtos": [asdict(p) for p in produtos],
            "vendas": [asdict(v) for v in vendas],
        }

    def load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                print("Arquivo de dados corrompido ou inválido. Criando um novo conjunto padrão.")
        
        data = self.default_data()
        self.save_data_direct(data)
        return data

    def save_data(self) -> None:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def save_data_direct(self, data: Dict[str, Any]) -> None:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get_supplier_name(self, supplier_id: int) -> str:
        return next((f["nome_empresa"] for f in self.data["fornecedores"] if f["id"] == supplier_id), "-")

    def sales_for_product(self, produto_id: int) -> List[Dict[str, Any]]:
        return [v for v in self.data["vendas"] if v["produto_id"] == produto_id]

    def estimate_daily_sales(self, sales: List[Dict[str, Any]], window_days: int = DEFAULT_WINDOW_DAYS) -> float:
        if not sales:
            return 0.0

        now = datetime.now()
        cutoff = now - timedelta(days=window_days)
        weighted_sales = []
        for sale in sales:
            venda_dt = parse_datetime(sale["data_venda"])
            days_ago = (now - venda_dt).days
            if days_ago < 0:
                days_ago = 0
            if venda_dt >= cutoff:
                weight = 1.0 - (days_ago / window_days)
                weighted_sales.append(sale["quantidade"] * max(weight, 0.1))

        if weighted_sales:
            return sum(weighted_sales) / window_days

        total_quantity = sum(sale["quantidade"] for sale in sales)
        earliest = min(parse_datetime(sale["data_venda"]) for sale in sales)
        total_days = max(1, (now - earliest).days)
        return total_quantity / total_days

    def estimate_monthly_sales(self, sales: List[Dict[str, Any]]) -> float:
        if not sales:
            return 0.0
        dates = [parse_datetime(v["data_venda"]) for v in sales]
        first = min(dates)
        last = max(dates)
        months = max(1, (last.year - first.year) * 12 + last.month - first.month + 1)
        total_quantity = sum(v["quantidade"] for v in sales)
        return total_quantity / months

    def predict_stock_depletion(self, produto: Dict[str, Any]) -> Optional[float]:
        sales = self.sales_for_product(produto["id"])
        daily_sales = self.estimate_daily_sales(sales)
        if daily_sales <= 0:
            return None
        return produto["quantidade_atual"] / daily_sales

    def suggest_optimal_price(self, produto: Dict[str, Any]) -> float:
        sales = self.sales_for_product(produto["id"])
        cost = produto["preco_custo"]
        current_price = produto["preco_venda"]
        monthly_sales = self.estimate_monthly_sales(sales)

        base_markup = 1.25
        if monthly_sales >= 20:
            base_markup = 1.50
        elif monthly_sales >= 10:
            base_markup = 1.40
        elif monthly_sales >= 5:
            base_markup = 1.30

        suggested = cost * base_markup
        min_price = max(cost * 1.15, current_price * 0.90)
        max_price = max(cost * 2.50, current_price * 1.15)
        suggested = min(max(suggested, min_price), max_price)

        if monthly_sales < 3 and current_price > suggested:
            suggested = max(min_price, current_price * 0.95)

        return round(suggested, 2)

    def save_product(self, product_id: Optional[int], name: str, description: str, 
                     preco_custo: float, preco_venda: float, 
                     quantidade_atual: int, quantidade_minima: int, 
                     fornecedor_nome: str) -> tuple[bool, str]:
        try:
            supplier = next((f for f in self.data["fornecedores"] if f["nome_empresa"] == fornecedor_nome), None)
            supplier_id = supplier["id"] if supplier else 0

            if product_id is None:
                new_id = max((p["id"] for p in self.data["produtos"]), default=0) + 1
                produto = {
                    "id": new_id,
                    "nome": name,
                    "descricao": description,
                    "preco_custo": preco_custo,
                    "preco_venda": preco_venda,
                    "quantidade_atual": quantidade_atual,
                    "quantidade_minima": quantidade_minima,
                    "fornecedor_id": supplier_id,
                    "atualizado_em": datetime.now().isoformat(timespec="seconds"),
                }
                self.data["produtos"].append(produto)
                msg = "Produto adicionado com sucesso."
            else:
                produto = next((p for p in self.data["produtos"] if p["id"] == product_id), None)
                if not produto:
                    return False, "Produto selecionado não foi encontrado."
                produto.update({
                    "nome": name,
                    "descricao": description,
                    "preco_custo": preco_custo,
                    "preco_venda": preco_venda,
                    "quantidade_atual": quantidade_atual,
                    "quantidade_minima": quantidade_minima,
                    "fornecedor_id": supplier_id,
                    "atualizado_em": datetime.now().isoformat(timespec="seconds"),
                })
                msg = "Produto atualizado com sucesso."

            self.save_data()
            return True, msg
        except Exception as e:
            return False, f"Erro interno ao salvar produto: {e}"

    def add_supplier(self, name: str, contact: str, phone: str, email: str) -> tuple[bool, str]:
        try:
            fornecedor_id = max((f["id"] for f in self.data["fornecedores"]), default=0) + 1
            supplier = {
                "id": fornecedor_id,
                "nome_empresa": name,
                "contato_nome": contact,
                "telefone": phone,
                "email": email,
                "criado_em": datetime.now().isoformat(timespec="seconds"),
            }
            self.data["fornecedores"].append(supplier)
            self.save_data()
            return True, "Fornecedor adicionado com sucesso."
        except Exception as e:
            return False, f"Erro interno ao adicionar fornecedor: {e}"

    def register_sale(self, produto_nome: str, quantidade: int) -> tuple[bool, str]:
        try:
            produto = next((p for p in self.data["produtos"] if p["nome"] == produto_nome), None)
            if not produto:
                return False, "Selecione um produto válido."

            if produto["quantidade_atual"] < quantidade:
                return False, f"Estoque insuficiente! Estoque atual: {produto['quantidade_atual']} unidade(s)."

            produto["quantidade_atual"] -= quantidade
            produto["atualizado_em"] = datetime.now().isoformat(timespec="seconds")

            venda_id = max((v["id"] for v in self.data["vendas"]), default=0) + 1
            venda = Venda(
                id=venda_id,
                produto_id=produto["id"],
                quantidade=quantidade,
                preco_unitario=produto["preco_venda"],
                data_venda=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            self.data["vendas"].append(asdict(venda))
            self.save_data()
            return True, f"Venda de {quantidade} unidade(s) de {produto_nome} registrada com sucesso."
        except Exception as e:
            return False, f"Erro interno ao registrar venda: {e}"

    def export_to_csv(self, path: str) -> tuple[bool, str]:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Produto;Quantidade;Mínimo;Dias até zerar;Preço atual;Preço sugerido;Fornecedor\n")
                for produto in self.data["produtos"]:
                    dias = self.predict_stock_depletion(produto)
                    suggested = self.suggest_optimal_price(produto)
                    f.write(
                        f"{produto['nome']};{produto['quantidade_atual']};{produto['quantidade_minima']};"
                        f"{format_depletion(dias)};{format_currency(produto['preco_venda'])};"
                        f"{format_currency(suggested)};{self.get_supplier_name(produto['fornecedor_id'])}\n"
                    )
            return True, f"Relatório salvo em:\n{path}"
        except OSError as error:
            return False, f"Não foi possível exportar o relatório:\n{error}"


# Funções Utilitárias Globais de Formatação
def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

def format_currency(value: float) -> str:
    return f"R$ {value:.2f}"

def format_depletion(days: Optional[float]) -> str:
    if days is None:
        return "Sem dados suficientes"
    if days < 1:
        return "Menos de 1 dia"
    return f"{days:.1f} dias"

def format_date(value: str) -> str:
    try:
        return parse_datetime(value).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value


def build_app(controller: StockController) -> Tk:
    root = Tk()
    root.title("StockPulse - Gerenciamento de Estoque")
    root.geometry("1020x620")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # --- PRODUTOS TAB ---
    frame_produtos = ttk.Frame(notebook)
    notebook.add(frame_produtos, text="Produtos")

    search_var = StringVar()
    ttk.Label(frame_produtos, text="Buscar produto:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
    search_entry = ttk.Entry(frame_produtos, textvariable=search_var)
    search_entry.grid(row=0, column=1, sticky="we", padx=8, pady=8)
    frame_produtos.columnconfigure(1, weight=1)

    product_columns = ("id", "nome", "quantidade_atual", "quantidade_minima", "preco_custo", "preco_venda", "fornecedor")
    product_tree = ttk.Treeview(frame_produtos, columns=product_columns, show="headings", selectmode="browse", height=12)
    for col in product_columns:
        product_tree.heading(col, text=col.replace("_", " ").title())
        product_tree.column(col, anchor=CENTER, width=120)
    product_tree.column("nome", width=260)
    product_tree.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
    frame_produtos.rowconfigure(1, weight=1)

    low_stock_label = Label(frame_produtos, text="")
    low_stock_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=8)

    detail_frame = ttk.LabelFrame(frame_produtos, text="Detalhes do Produto")
    detail_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)

    labels = ["Nome", "Descrição", "Preço de custo", "Preço de venda", "Quantidade atual", "Quantidade mínima", "Fornecedor"]
    fields = [StringVar() for _ in labels]
    fornecedor_combo: Optional[ttk.Combobox] = None
    for index, label_text in enumerate(labels):
        ttk.Label(detail_frame, text=label_text + ":").grid(row=index, column=0, padx=8, pady=6, sticky="e")
        if label_text == "Descrição":
            ttk.Entry(detail_frame, textvariable=fields[index], width=70).grid(row=index, column=1, padx=8, pady=6, sticky="w")
        elif label_text == "Fornecedor":
            fornecedores = [f["nome_empresa"] for f in controller.data["fornecedores"]]
            fornecedor_combo = ttk.Combobox(detail_frame, textvariable=fields[index], values=fornecedores, state="readonly", width=56)
            if fornecedores:
                fornecedor_combo.current(0)
            fornecedor_combo.grid(row=index, column=1, padx=8, pady=6, sticky="w")
        else:
            ttk.Entry(detail_frame, textvariable=fields[index], width=56).grid(row=index, column=1, padx=8, pady=6, sticky="w")

    selected_product_id: Optional[int] = None
    stats_text = StringVar(value="Selecione um produto para ver métricas.")
    ttk.Label(detail_frame, textvariable=stats_text, justify="left").grid(row=0, column=2, rowspan=7, padx=16, pady=8, sticky="nw")

    def get_selected_product() -> Optional[Dict[str, Any]]:
        selected = product_tree.selection()
        if not selected:
            return None
        produto_id = int(product_tree.item(selected[0])["values"][0])
        return next((p for p in controller.data["produtos"] if p["id"] == produto_id), None)

    def update_detail_panel(produto: Dict[str, Any]) -> None:
        nonlocal selected_product_id
        selected_product_id = produto["id"]
        fields[0].set(produto["nome"])
        fields[1].set(produto["descricao"])
        fields[2].set(f"{produto['preco_custo']:.2f}")
        fields[3].set(f"{produto['preco_venda']:.2f}")
        fields[4].set(str(produto["quantidade_atual"]))
        fields[5].set(str(produto["quantidade_minima"]))
        fields[6].set(controller.get_supplier_name(produto["fornecedor_id"]))

        vendas = controller.sales_for_product(produto["id"])
        daily = controller.estimate_daily_sales(vendas)
        monthly = controller.estimate_monthly_sales(vendas)
        dias = controller.predict_stock_depletion(produto)
        suggested = controller.suggest_optimal_price(produto)
        reorder = max(0, produto["quantidade_minima"] * 2 - produto["quantidade_atual"])

        stats_text.set(
            f"Vendas médias/dia: {daily:.2f}\n"
            f"Vendas médias/mês: {monthly:.2f}\n"
            f"Estoque atual: {produto['quantidade_atual']}\n"
            f"Estoque mínimo: {produto['quantidade_minima']}\n"
            f"Previsão de esgotamento: {format_depletion(dias)}\n"
            f"Sugestão de preço: {format_currency(suggested)}\n"
            f"Quantidade recomendada para repor: {reorder}\n"
            f"Fornecedor: {controller.get_supplier_name(produto['fornecedor_id'])}"
        )

    def refresh_products(event: Optional[Any] = None) -> None:
        query = search_var.get().strip().lower()
        for item in product_tree.get_children():
            product_tree.delete(item)

        low_stock = []
        for produto in controller.data["produtos"]:
            if query and query not in produto["nome"].lower() and query not in produto["descricao"].lower():
                continue
            fornecedor_nome = controller.get_supplier_name(produto["fornecedor_id"])
            product_tree.insert(
                "",
                END,
                values=(
                    produto["id"],
                    produto["nome"],
                    produto["quantidade_atual"],
                    produto["quantidade_minima"],
                    format_currency(produto["preco_custo"]),
                    format_currency(produto["preco_venda"]),
                    fornecedor_nome,
                ),
            )
            if produto["quantidade_atual"] <= produto["quantidade_minima"]:
                low_stock.append(produto["nome"])

        if low_stock:
            low_stock_label.config(text=f"Atenção: estoque baixo para {', '.join(low_stock)}.")
        else:
            low_stock_label.config(text="Todos os produtos acima do estoque mínimo.")

    def on_product_select(event: Any) -> None:
        produto = get_selected_product()
        if produto:
            update_detail_panel(produto)

    product_tree.bind("<<TreeviewSelect>>", on_product_select)
    search_entry.bind("<KeyRelease>", refresh_products)

    def refresh_comboboxes() -> None:
        product_names = [p["nome"] for p in controller.data["produtos"]]
        sale_product_combo["values"] = product_names
        if product_names and sale_product_var.get() not in product_names:
            sale_product_combo.current(0)

        supplier_names = [f["nome_empresa"] for f in controller.data["fornecedores"]]
        if fornecedor_combo is not None:
            fornecedor_combo["values"] = supplier_names
            if supplier_names and fields[6].get() not in supplier_names:
                fields[6].set(supplier_names[0])

    def validate_float(value: str) -> Optional[float]:
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None

    def validate_int(value: str) -> Optional[int]:
        try:
            return int(value)
        except ValueError:
            return None

    def save_product() -> None:
        nonlocal selected_product_id
        name = fields[0].get().strip()
        description = fields[1].get().strip()
        preco_custo = validate_float(fields[2].get().strip())
        preco_venda = validate_float(fields[3].get().strip())
        quantidade_atual = validate_int(fields[4].get().strip())
        quantidade_minima = validate_int(fields[5].get().strip())
        fornecedor_nome = fields[6].get().strip()

        if not name:
            messagebox.showwarning("Validar produto", "Informe o nome do produto.")
            return
        if preco_custo is None or preco_custo <= 0:
            messagebox.showwarning("Validar produto", "Informe um preço de custo válido.")
            return
        if preco_venda is None or preco_venda <= 0:
            messagebox.showwarning("Validar produto", "Informe um preço de venda válido.")
            return
        if quantidade_atual is None or quantidade_atual < 0:
            messagebox.showwarning("Validar produto", "Informe a quantidade atual.")
            return
        if quantidade_minima is None or quantidade_minima < 0:
            messagebox.showwarning("Validar produto", "Informe a quantidade mínima.")
            return

        success, msg = controller.save_product(
            selected_product_id, name, description, preco_custo, preco_venda, 
            quantidade_atual, quantidade_minima, fornecedor_nome
        )

        if success:
            messagebox.showinfo("Sucesso", msg)
            refresh_products()
            refresh_forecast_table()
            refresh_comboboxes()
            if selected_product_id is None:
                clear_selection()
        else:
            messagebox.showerror("Erro", msg)

    def clear_selection() -> None:
        nonlocal selected_product_id
        selected_product_id = None
        for field in fields:
            field.set("")
        if controller.data["fornecedores"]:
            fields[6].set(controller.data["fornecedores"][0]["nome_empresa"])
        stats_text.set("Informe os dados do produto e clique em Salvar Produto.")
        product_tree.selection_remove(product_tree.selection())

    def handle_export_csv() -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Exportar relatório de estoque",
        )
        if not path:
            return
        success, msg = controller.export_to_csv(path)
        if success:
            messagebox.showinfo("Exportado", msg)
        else:
            messagebox.showerror("Erro", msg)

    btn_save_product = ttk.Button(detail_frame, text="Salvar Produto", command=save_product)
    btn_save_product.grid(row=8, column=0, padx=8, pady=10, sticky="w")

    btn_clear_product = ttk.Button(detail_frame, text="Limpar campos", command=clear_selection)
    btn_clear_product.grid(row=8, column=1, padx=8, pady=10, sticky="w")

    btn_export = ttk.Button(detail_frame, text="Exportar relatório", command=handle_export_csv)
    btn_export.grid(row=8, column=2, padx=8, pady=10, sticky="w")

    # --- FORNECEDORES TAB ---
    frame_fornecedores = ttk.Frame(notebook)
    notebook.add(frame_fornecedores, text="Fornecedores")

    supplier_columns = ("id", "nome_empresa", "contato_nome", "telefone", "email")
    supplier_tree = ttk.Treeview(frame_fornecedores, columns=supplier_columns, show="headings", selectmode="none", height=12)
    for col in supplier_columns:
        supplier_tree.heading(col, text=col.replace("_", " ").title())
        supplier_tree.column(col, anchor=CENTER, width=160)
    supplier_tree.column("nome_empresa", width=240)
    supplier_tree.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
    frame_fornecedores.rowconfigure(0, weight=1)
    frame_fornecedores.columnconfigure(0, weight=1)

    supplier_name_var = StringVar()
    supplier_contact_var = StringVar()
    supplier_phone_var = StringVar()
    supplier_email_var = StringVar()

    ttk.Label(frame_fornecedores, text="Empresa:").grid(row=1, column=0, sticky="e", padx=8, pady=4)
    ttk.Entry(frame_fornecedores, textvariable=supplier_name_var, width=30).grid(row=1, column=1, sticky="w", padx=8, pady=4)
    ttk.Label(frame_fornecedores, text="Contato:").grid(row=1, column=2, sticky="e", padx=8, pady=4)
    ttk.Entry(frame_fornecedores, textvariable=supplier_contact_var, width=30).grid(row=1, column=3, sticky="w", padx=8, pady=4)

    ttk.Label(frame_fornecedores, text="Telefone:").grid(row=2, column=0, sticky="e", padx=8, pady=4)
    ttk.Entry(frame_fornecedores, textvariable=supplier_phone_var, width=30).grid(row=2, column=1, sticky="w", padx=8, pady=4)
    ttk.Label(frame_fornecedores, text="Email:").grid(row=2, column=2, sticky="e", padx=8, pady=4)
    ttk.Entry(frame_fornecedores, textvariable=supplier_email_var, width=30).grid(row=2, column=3, sticky="w", padx=8, pady=4)

    def refresh_suppliers() -> None:
        for item in supplier_tree.get_children():
            supplier_tree.delete(item)
        for sup in controller.data["fornecedores"]:
            supplier_tree.insert("", END, values=(sup["id"], sup["nome_empresa"], sup["contato_nome"], sup["telefone"], sup["email"]))

    def add_supplier() -> None:
        name = supplier_name_var.get().strip()
        contact = supplier_contact_var.get().strip()
        phone = supplier_phone_var.get().strip()
        email = supplier_email_var.get().strip()
        if not name:
            messagebox.showwarning("Validar fornecedor", "Informe o nome da empresa.")
            return

        success, msg = controller.add_supplier(name, contact, phone, email)
        if success:
            messagebox.showinfo("Fornecedor criado", msg)
            refresh_suppliers()
            refresh_comboboxes()
            if fields[6].get() == "":
                fields[6].set(name)
            supplier_name_var.set("")
            supplier_contact_var.set("")
            supplier_phone_var.set("")
            supplier_email_var.set("")
        else:
            messagebox.showerror("Erro", msg)

    btn_add_supplier = ttk.Button(frame_fornecedores, text="Adicionar fornecedor", command=add_supplier)
    btn_add_supplier.grid(row=3, column=0, columnspan=4, pady=8)

    # --- VENDAS TAB ---
    frame_sales = ttk.Frame(notebook)
    notebook.add(frame_sales, text="Vendas")

    sale_product_var = StringVar()
    sale_quantity_var = StringVar()

    ttk.Label(frame_sales, text="Produto:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
    produto_names = [p["nome"] for p in controller.data["produtos"]]
    sale_product_combo = ttk.Combobox(frame_sales, textvariable=sale_product_var, values=produto_names, state="readonly", width=40)
    sale_product_combo.grid(row=0, column=1, padx=8, pady=8, sticky="w")
    if produto_names:
        sale_product_combo.current(0)

    ttk.Label(frame_sales, text="Quantidade:").grid(row=0, column=2, padx=8, pady=8, sticky="e")
    ttk.Entry(frame_sales, textvariable=sale_quantity_var, width=10).grid(row=0, column=3, padx=8, pady=8, sticky="w")

    sales_columns = ("id", "produto", "quantidade", "preco", "data")
    sales_tree = ttk.Treeview(frame_sales, columns=sales_columns, show="headings", selectmode="none", height=12)
    for col in sales_columns:
        sales_tree.heading(col, text=col.title())
        sales_tree.column(col, anchor=CENTER, width=120)
    sales_tree.column("produto", width=260)
    sales_tree.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
    frame_sales.rowconfigure(1, weight=1)
    frame_sales.columnconfigure(1, weight=1)

    def refresh_sales_history() -> None:
        for item in sales_tree.get_children():
            sales_tree.delete(item)
        recent = sorted(controller.data["vendas"], key=lambda v: parse_datetime(v["data_venda"]), reverse=True)
        for venda in recent[:15]:
            produto_nome = next((p["nome"] for p in controller.data["produtos"] if p["id"] == venda["produto_id"]), "-")
            sales_tree.insert(
                "",
                END,
                values=(
                    venda["id"],
                    produto_nome,
                    venda["quantidade"],
                    format_currency(venda["preco_unitario"]),
                    format_date(venda["data_venda"]),
                ),
            )

    def register_sale() -> None:
        produto_nome = sale_product_var.get()
        quantidade = validate_int(sale_quantity_var.get().strip())
        if quantidade is None or quantidade <= 0:
            messagebox.showwarning("Entrada inválida", "Informe uma quantidade inteira maior que zero.")
            return

        success, msg = controller.register_sale(produto_nome, quantidade)
        if success:
            messagebox.showinfo("Venda registrada", msg)
            sale_quantity_var.set("")
            refresh_sales_history()
            refresh_products()
            refresh_forecast_table()
        else:
            messagebox.showwarning("Atenção", msg)

    btn_register_sale = ttk.Button(frame_sales, text="Registrar venda", command=register_sale)
    btn_register_sale.grid(row=2, column=0, columnspan=4, pady=8)

    # --- FORECAST TAB ---
    frame_forecast = ttk.Frame(notebook)
    notebook.add(frame_forecast, text="Previsões")

    forecast_columns = ("nome", "quantidade_atual", "quantidade_minima", "dias_restantes", "repor", "preco_atual", "preco_sugerido")
    forecast_tree = ttk.Treeview(frame_forecast, columns=forecast_columns, show="headings", selectmode="none", height=15)
    for col in forecast_columns:
        forecast_tree.heading(col, text=col.replace("_", " ").title())
        forecast_tree.column(col, anchor=CENTER, width=120)
    forecast_tree.column("nome", width=260)
    forecast_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    frame_forecast.rowconfigure(0, weight=1)
    frame_forecast.columnconfigure(0, weight=1)

    def refresh_forecast_table() -> None:
        for item in forecast_tree.get_children():
            forecast_tree.delete(item)
        for produto in controller.data["produtos"]:
            dias = controller.predict_stock_depletion(produto)
            repor = max(0, produto["quantidade_minima"] * 2 - produto["quantidade_atual"])
            preco_sugerido = controller.suggest_optimal_price(produto)
            forecast_tree.insert(
                "",
                END,
                values=(
                    produto["nome"],
                    produto["quantidade_atual"],
                    produto["quantidade_minima"],
                    format_depletion(dias),
                    repor,
                    format_currency(produto["preco_venda"]),
                    format_currency(preco_sugerido),
                ),
            )

    # Inicialização das views
    refresh_products()
    refresh_forecast_table()
    refresh_sales_history()
    refresh_suppliers()

    return root


if __name__ == "__main__":
    stock_controller = StockController()
    app = build_app(stock_controller)
    app.mainloop()