"""
Testes para o Projeto Final da API Lanchonete

Este arquivo contém todos os testes obrigatórios para as funcionalidades:
- Cancelamento de pedido
- Observação do pedido
- Prioridade de pedido
- Fila de preparo
"""


def test_deve_cancelar_pedido(client):
    """Verifica que um pedido ativo pode ser cancelado com sucesso.

    Cenário:
        Um cliente, produto e pedido são criados. O pedido é cancelado
        via POST /{cod_pedido}/cancelar.

    Resultado esperado:
        - Status HTTP 200
        - Corpo com ok=True
    """
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = client.post(f"/lanchonete/pedidos/{cod_pedido}/cancelar")

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


def test_nao_deve_cancelar_pedido_entregue(client):
    """Garante que um pedido entregue não pode ser cancelado.

    Cenário:
        Um pedido é criado e finalizado (entregue). Em seguida, tenta-se
        cancelá-lo.

    Regra de negócio:
        Pedidos entregues não podem ser cancelados.

    Resultado esperado:
        - Status HTTP 400
        - Mensagem indicando que o pedido não pode ser cancelado
    """
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]
    client.post(f"/lanchonete/pedidos/{cod_pedido}/finalizar")

    response = client.post(f"/lanchonete/pedidos/{cod_pedido}/cancelar")

    assert response.status_code == 400


def test_deve_adicionar_observacao(client):
    """Verifica que uma observação pode ser adicionada com sucesso.

    Cenário:
        Um pedido é criado e uma observação "Sem cebola" é adicionada
        via POST /{cod_pedido}/observacao.

    Resultado esperado:
        - Status HTTP 200
        - Corpo com ok=True
    """
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = client.post(
        f"/lanchonete/pedidos/{cod_pedido}/observacao",
        json={"observacao": "Sem cebola"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


def test_nao_deve_aceitar_observacao_vazia(client):
    """Garante que uma observação vazia é rejeitada.

    Cenário:
        Um pedido é criado e o endpoint é chamado com observacao="".

    Regra de negócio:
        Observações vazias ou compostas só de espaços não são permitidas.

    Resultado esperado:
        - Status HTTP 400
        - Mensagem de erro indicando pedido inválido
    """
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = client.post(
        f"/lanchonete/pedidos/{cod_pedido}/observacao",
        json={"observacao": ""},
    )

    assert response.status_code == 400


def test_deve_tornar_pedido_prioritario(client):
    """Verifica que um pedido ativo pode ser marcado como prioritário.

    Cenário:
        Um pedido é criado e marcado como prioritário via
        POST /{cod_pedido}/prioridade.

    Resultado esperado:
        - Status HTTP 200
        - Corpo com ok=True
    """
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})
    r = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido = r.json()["codigo"]

    response = client.post(f"/lanchonete/pedidos/{cod_pedido}/prioridade")

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


def test_fila_deve_ter_prioritarios_primeiro(client):
    """Verifica que pedidos prioritários aparecem primeiro na fila.

    Cenário:
        3 pedidos são criados:
        - Pedido 1 (normal)
        - Pedido 2 (prioritário)
        - Pedido 3 (normal)

        A fila de preparo é consultada.

    Resultado esperado:
        - Pedido 2 (prioritário) deve aparecer primeiro
        - Depois Pedido 1 (normal)
        - Depois Pedido 3 (normal)
    """
    # Criar cliente e produto
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})

    # Criar 3 pedidos
    r1 = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido1 = r1.json()["codigo"]

    r2 = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido2 = r2.json()["codigo"]

    r3 = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido3 = r3.json()["codigo"]

    # Tornar pedido 2 prioritário
    client.post(f"/lanchonete/pedidos/{cod_pedido2}/prioridade")

    # Consultar fila
    response = client.get("/lanchonete/pedidos/fila/preparo")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Verificar ordem: prioritário primeiro
    assert data[0]["codigo"] == cod_pedido2
    assert data[0]["prioritario"] is True
    assert data[1]["codigo"] == cod_pedido1
    assert data[1]["prioritario"] is False
    assert data[2]["codigo"] == cod_pedido3
    assert data[2]["prioritario"] is False


def test_fila_nao_deve_listar_cancelados(client):
    """Verifica que pedidos cancelados não aparecem na fila.

    Cenário:
        2 pedidos são criados:
        - Pedido 1 (ativo)
        - Pedido 2 (será cancelado)

        A fila de preparo é consultada.

    Resultado esperado:
        - Apenas Pedido 1 deve aparecer na fila
        - Pedido 2 não deve aparecer
    """
    # Criar cliente e produto
    client.post("/clientes", json={"cpf": "12345678900", "nome": "Joao"})
    client.post("/produtos", json={"codigo": 1, "valor": 10.0, "tipo": 2})

    # Criar 2 pedidos
    r1 = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido1 = r1.json()["codigo"]

    r2 = client.post("/lanchonete/pedidos", json={"cpf": "12345678900", "cod_produto": 1, "qtd_max_produtos": 5})
    cod_pedido2 = r2.json()["codigo"]

    # Cancelar pedido 2
    client.post(f"/lanchonete/pedidos/{cod_pedido2}/cancelar")

    # Consultar fila
    response = client.get("/lanchonete/pedidos/fila/preparo")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["codigo"] == cod_pedido1
