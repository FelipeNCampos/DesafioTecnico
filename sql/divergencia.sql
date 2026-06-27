-- Relatorio de divergencia:
-- compara as duas ultimas contagens de cada produto em um endereco.
WITH ranked AS (
    SELECT
        p.codigo AS sku,
        p.descricao AS produto,
        c.quantidade,
        c.contado_em,
        ROW_NUMBER() OVER (
            PARTITION BY c.produto_id
            ORDER BY c.contado_em DESC, c.id DESC
        ) AS rn
    FROM contagens c
    INNER JOIN produtos p ON p.id = c.produto_id
    INNER JOIN enderecos e ON e.id = c.endereco_id
    WHERE e.codigo = :codigo_endereco
),
ultimas AS (
    SELECT
        sku,
        produto,
        MAX(CASE WHEN rn = 1 THEN quantidade END) AS quantidade_atual,
        MAX(CASE WHEN rn = 2 THEN quantidade END) AS quantidade_anterior,
        MAX(CASE WHEN rn = 1 THEN contado_em END) AS contado_em_atual,
        MAX(CASE WHEN rn = 2 THEN contado_em END) AS contado_em_anterior,
        COUNT(*) AS total_contagens
    FROM ranked
    WHERE rn <= 2
    GROUP BY sku, produto
)
SELECT
    sku,
    produto,
    quantidade_atual,
    quantidade_anterior,
    CASE
        WHEN total_contagens < 2 THEN NULL
        ELSE quantidade_atual - quantidade_anterior
    END AS diferenca,
    CASE
        WHEN total_contagens < 2 THEN 'sem_historico'
        WHEN quantidade_atual - quantidade_anterior > 0 THEN 'aumento'
        WHEN quantidade_atual - quantidade_anterior < 0 THEN 'reducao'
        ELSE 'estavel'
    END AS status,
    contado_em_atual,
    contado_em_anterior
FROM ultimas
ORDER BY sku;
