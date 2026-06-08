-- 1. Criação do Banco de Dados
CREATE DATABASE IF NOT EXISTS stockpulse;
USE stockpulse;

-- 2. Tabela de Usuários (para o login no Electron)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL, -- Guardar sempre a senha criptografada (hash)
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela de Fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_empresa VARCHAR(150) NOT NULL,
    contato_nome VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela de Produtos (Estoque)
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    preco_custo DECIMAL(10, 2) NOT NULL,
    preco_venda DECIMAL(10, 2) NOT NULL,
    quantidade_atual INT NOT NULL DEFAULT 0,
    quantidade_minima INT NOT NULL DEFAULT 10, -- Gatilho para o Electron alertar "Estoque Baixo"
    fornecedor_id INT,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL
);

-- 5. Tabela de Vendas (Histórico essencial para a IA em Python prever a demanda)
CREATE TABLE IF NOT EXISTS vendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

-- Inserindo um Fornecedor
INSERT INTO fornecedores (nome_empresa, contato_nome, telefone, email) VALUES
('Tech Distribuidora Ltda', 'Carlos Silva', '(11) 99999-1111', 'carlos@techdist.com');

-- Inserindo Produtos (Note o estoque baixo no Produto 2 para testar o alerta no Electron)
INSERT INTO produtos (nome, descricao, preco_custo, preco_venda, quantidade_atual, quantidade_minima, fornecedor_id) VALUES
('Teclado Mecânico RGB', 'Teclado switch azul layout ABNT2', 120.00, 250.00, 45, 15, 1),
('Mouse Gamer Pro', 'Mouse 16000 DPI sensor óptico', 80.00, 180.00, 8, 12, 1); -- Quantidade (8) menor que a mínima (12)

-- Inserindo Histórico de Vendas simulado (Simulando uma crescente para o algoritmo do Python prever)
INSERT INTO vendas (produto_id, quantidade, preco_unitario, data_venda) VALUES
(1, 5, 250.00, '2026-03-01 14:00:00'),
(1, 8, 250.00, '2026-04-01 10:30:00'),
(1, 12, 250.00, '2026-05-01 16:15:00'), -- Vendas subindo mês a mês
(2, 2, 180.00, '2026-05-10 11:00:00'),
(2, 4, 180.00, '2026-06-01 09:45:00');