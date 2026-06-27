(function () {
    const SESSION_KEY = "estoqueX.session";
    const DASHBOARD_REFRESH_MS = 3000;

    const state = {
        session: null,
        refreshTimer: null,
        isDashboardLoading: false,
        products: [],
        addresses: [],
        productSearchTimer: null,
        addressSearchTimer: null,
        stockAddressSearchTimer: null,
        reportAddressSearchTimer: null,
        productPage: 1,
        productPages: 1,
        addressPage: 1,
        addressPages: 1,
        perPage: 5,
    };

    const els = {
        loginView: document.getElementById("loginView"),
        dashboardView: document.getElementById("dashboardView"),
        loginForm: document.getElementById("loginForm"),
        loginButton: document.getElementById("loginButton"),
        loginAlert: document.getElementById("loginAlert"),
        logoutButton: document.getElementById("logoutButton"),
        navUserBadge: document.getElementById("navUserBadge"),
        dashboardAlert: document.getElementById("dashboardAlert"),
        welcomeTitle: document.getElementById("welcomeTitle"),
        welcomeSubtitle: document.getElementById("welcomeSubtitle"),
        productsTotal: document.getElementById("productsTotal"),
        addressesTotal: document.getElementById("addressesTotal"),
        productsTableBody: document.getElementById("productsTableBody"),
        addressesTableBody: document.getElementById("addressesTableBody"),
        productsEmpty: document.getElementById("productsEmpty"),
        addressesEmpty: document.getElementById("addressesEmpty"),
        productsPageInfo: document.getElementById("productsPageInfo"),
        addressesPageInfo: document.getElementById("addressesPageInfo"),
        prevProductsButton: document.getElementById("prevProductsButton"),
        nextProductsButton: document.getElementById("nextProductsButton"),
        prevAddressesButton: document.getElementById("prevAddressesButton"),
        nextAddressesButton: document.getElementById("nextAddressesButton"),
        stockShortcutForm: document.getElementById("stockShortcutForm"),
        stockAddressInput: document.getElementById("stockAddressInput"),
        stockAddressOptions: document.getElementById("stockAddressOptions"),
        stockResult: document.getElementById("stockResult"),
        reportShortcutForm: document.getElementById("reportShortcutForm"),
        reportAddressInput: document.getElementById("reportAddressInput"),
        reportAddressOptions: document.getElementById("reportAddressOptions"),
        reportButton: document.getElementById("reportButton"),
        reportResult: document.getElementById("reportResult"),
        productForm: document.getElementById("productForm"),
        productFormAlert: document.getElementById("productFormAlert"),
        saveProductButton: document.getElementById("saveProductButton"),
        addressForm: document.getElementById("addressForm"),
        addressFormAlert: document.getElementById("addressFormAlert"),
        saveAddressButton: document.getElementById("saveAddressButton"),
        countForm: document.getElementById("countForm"),
        countFormAlert: document.getElementById("countFormAlert"),
        saveCountButton: document.getElementById("saveCountButton"),
        productModal: document.getElementById("productModal"),
        addressModal: document.getElementById("addressModal"),
        countModal: document.getElementById("countModal"),
        countProductInput: document.getElementById("countProductInput"),
        countAddressInput: document.getElementById("countAddressInput"),
        productOptions: document.getElementById("productOptions"),
        addressOptions: document.getElementById("addressOptions"),
    };

    function getStoredSession() {
        const rawSession = sessionStorage.getItem(SESSION_KEY);
        if (!rawSession) {
            return null;
        }

        try {
            const session = JSON.parse(rawSession);
            if (!session.access_token || !session.user) {
                return null;
            }
            return session;
        } catch (error) {
            return null;
        }
    }

    function storeSession(session) {
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
        state.session = session;
    }

    function clearSession() {
        sessionStorage.removeItem(SESSION_KEY);
        state.session = null;
        stopDashboardRefresh();
    }

    function showAlert(element, message) {
        element.textContent = message;
        element.classList.remove("d-none");
    }

    function hideAlert(element) {
        element.textContent = "";
        element.classList.add("d-none");
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    async function parseResponse(response) {
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
            return response.json();
        }
        return {};
    }

    async function apiFetch(path, options) {
        const requestOptions = {
            ...options,
            headers: {
                ...(options && options.headers ? options.headers : {}),
            },
        };

        if (state.session && state.session.access_token) {
            requestOptions.headers.Authorization = `Bearer ${state.session.access_token}`;
        }

        const response = await fetch(path, requestOptions);
        const payload = await parseResponse(response);

        if ((response.status === 401 || response.status === 422) && path !== "/auth/login") {
            clearSession();
            render();
            throw new Error("Sessao expirada. Entre novamente.");
        }

        if (!response.ok) {
            throw new Error(payload.message || "Nao foi possivel concluir a requisicao.");
        }

        return payload;
    }

    function getModal(element) {
        return bootstrap.Modal.getOrCreateInstance(element);
    }

    function resetForm(form, alertElement) {
        form.reset();
        hideAlert(alertElement);
    }

    function startDashboardRefresh() {
        if (state.refreshTimer) {
            return;
        }
        state.refreshTimer = window.setInterval(() => {
            if (state.session) {
                loadDashboard();
            }
        }, DASHBOARD_REFRESH_MS);
    }

    function stopDashboardRefresh() {
        if (!state.refreshTimer) {
            return;
        }
        window.clearInterval(state.refreshTimer);
        state.refreshTimer = null;
    }

    function renderLogin() {
        stopDashboardRefresh();
        els.dashboardView.classList.add("d-none");
        els.loginView.classList.remove("d-none");
        els.logoutButton.classList.add("d-none");
        els.navUserBadge.classList.add("d-none");
        els.navUserBadge.textContent = "";
    }

    function renderDashboard() {
        const user = state.session.user;
        const isManager = user.perfil === "gerente";

        els.loginView.classList.add("d-none");
        els.dashboardView.classList.remove("d-none");
        els.logoutButton.classList.remove("d-none");
        els.navUserBadge.classList.remove("d-none");
        els.navUserBadge.textContent = `${user.nome} - ${user.perfil}`;
        els.welcomeTitle.textContent = `Bem-vindo, ${user.nome}`;
        els.welcomeSubtitle.textContent = `Perfil ${user.perfil}. Dados carregados pela API protegida.`;

        document.querySelectorAll(".gerente-only").forEach((element) => {
            element.classList.toggle("d-none", !isManager);
        });
        els.reportButton.disabled = !isManager;
        startDashboardRefresh();
    }

    function render() {
        hideAlert(els.loginAlert);
        hideAlert(els.dashboardAlert);

        if (!state.session) {
            renderLogin();
            return;
        }

        renderDashboard();
        loadDashboard();
    }

    function renderProducts(payload) {
        const items = payload.items || [];
        state.products = items;
        state.productPage = payload.page || state.productPage;
        state.productPages = Math.max(payload.pages || 1, 1);
        els.productsTotal.textContent = payload.total ?? items.length;
        els.productsPageInfo.textContent = `Pagina ${state.productPage} de ${state.productPages}`;
        els.prevProductsButton.disabled = state.productPage <= 1;
        els.nextProductsButton.disabled = state.productPage >= state.productPages;
        els.productsTableBody.innerHTML = items.map((item) => (
            `<tr>
                <td class="fw-semibold">${escapeHtml(item.codigo)}</td>
                <td>${escapeHtml(item.descricao)}</td>
                <td>${escapeHtml(item.unidade)}</td>
            </tr>`
        )).join("");
        els.productsEmpty.classList.toggle("d-none", items.length > 0);
    }

    function renderAddresses(payload) {
        const items = payload.items || [];
        state.addresses = items;
        state.addressPage = payload.page || state.addressPage;
        state.addressPages = Math.max(payload.pages || 1, 1);
        els.addressesTotal.textContent = payload.total ?? items.length;
        els.addressesPageInfo.textContent = `Pagina ${state.addressPage} de ${state.addressPages}`;
        els.prevAddressesButton.disabled = state.addressPage <= 1;
        els.nextAddressesButton.disabled = state.addressPage >= state.addressPages;
        els.addressesTableBody.innerHTML = items.map((item) => (
            `<tr>
                <td class="fw-semibold">${escapeHtml(item.codigo)}</td>
                <td>${escapeHtml(item.descricao || "-")}</td>
            </tr>`
        )).join("");
        els.addressesEmpty.classList.toggle("d-none", items.length > 0);
    }

    async function loadProducts() {
        const payload = await apiFetch(`/api/produtos?page=${state.productPage}&per_page=${state.perPage}`);
        renderProducts(payload);
    }

    async function loadAddresses() {
        const payload = await apiFetch(`/api/enderecos?page=${state.addressPage}&per_page=${state.perPage}`);
        renderAddresses(payload);
    }

    async function loadDashboard() {
        if (state.isDashboardLoading) {
            return;
        }
        state.isDashboardLoading = true;
        try {
            await Promise.all([loadProducts(), loadAddresses()]);
        } catch (error) {
            showAlert(els.dashboardAlert, error.message);
        } finally {
            state.isDashboardLoading = false;
        }
    }

    function renderResult(element, title, payload) {
        element.innerHTML = `<strong>${escapeHtml(title)}</strong><pre class="mt-2">${escapeHtml(JSON.stringify(payload, null, 2))}</pre>`;
        element.classList.remove("d-none");
    }

    async function searchProducts(query) {
        const params = new URLSearchParams({ page: "1", per_page: "10" });
        if (query) {
            params.set("q", query);
        }
        const payload = await apiFetch(`/api/produtos?${params.toString()}`);
        return payload.items || [];
    }

    async function searchAddresses(query) {
        const params = new URLSearchParams({ page: "1", per_page: "10" });
        if (query) {
            params.set("q", query);
        }
        const payload = await apiFetch(`/api/enderecos?${params.toString()}`);
        return payload.items || [];
    }

    function renderOptions(menu, items, getValue, getLabel, input) {
        if (!items.length) {
            menu.innerHTML = '<button class="list-group-item list-group-item-action text-secondary" type="button" disabled>Nenhuma correspondencia</button>';
            menu.classList.remove("d-none");
            return;
        }

        menu.innerHTML = items.map((item, index) => (
            `<button class="list-group-item list-group-item-action" type="button" data-index="${index}">
                ${escapeHtml(getLabel(item))}
            </button>`
        )).join("");

        Array.from(menu.querySelectorAll("button[data-index]")).forEach((button) => {
            button.addEventListener("click", () => {
                const item = items[Number(button.dataset.index)];
                input.value = getValue(item);
                menu.classList.add("d-none");
            });
        });

        menu.classList.remove("d-none");
    }

    function renderProductOptions(items) {
        renderOptions(
            els.productOptions,
            items,
            (item) => item.codigo,
            (item) => `${item.codigo} - ${item.descricao}`,
            els.countProductInput
        );
    }

    function renderAddressOptions(items) {
        renderOptions(
            els.addressOptions,
            items,
            (item) => item.codigo,
            (item) => `${item.codigo} - ${item.descricao || "Sem descricao"}`,
            els.countAddressInput
        );
    }

    function scheduleProductSearch() {
        window.clearTimeout(state.productSearchTimer);
        state.productSearchTimer = window.setTimeout(async () => {
            try {
                const items = await searchProducts(els.countProductInput.value.trim());
                renderProductOptions(items);
            } catch (error) {
                showAlert(els.countFormAlert, error.message);
            }
        }, 180);
    }

    function scheduleAddressSearch(input, menu, timerName, alertElement) {
        window.clearTimeout(state[timerName]);
        state[timerName] = window.setTimeout(async () => {
            try {
                const items = await searchAddresses(input.value.trim());
                renderOptions(
                    menu,
                    items,
                    (item) => item.codigo,
                    (item) => `${item.codigo} - ${item.descricao || "Sem descricao"}`,
                    input
                );
            } catch (error) {
                showAlert(alertElement, error.message);
            }
        }, 180);
    }

    async function resolveProductCode(value) {
        const text = value.trim();
        const normalized = text.toLowerCase();
        const items = await searchProducts(text);
        const exact = items.find((item) => (
            item.codigo.toLowerCase() === normalized ||
            item.descricao.toLowerCase() === normalized
        ));

        if (exact) {
            return exact.codigo;
        }
        if (items.length === 1) {
            return items[0].codigo;
        }
        if (items.length > 1) {
            throw new Error("Selecione um produto da lista.");
        }
        return text;
    }

    async function resolveAddressCode(value) {
        const text = value.trim();
        const normalized = text.toLowerCase();
        const items = await searchAddresses(text);
        const exact = items.find((item) => (
            item.codigo.toLowerCase() === normalized ||
            String(item.descricao || "").toLowerCase() === normalized
        ));

        if (exact) {
            return exact.codigo;
        }
        if (items.length === 1) {
            return items[0].codigo;
        }
        if (items.length > 1) {
            throw new Error("Selecione um endereco da lista.");
        }
        return text;
    }

    async function handleLogin(event) {
        event.preventDefault();
        hideAlert(els.loginAlert);

        const formData = new FormData(els.loginForm);
        const email = String(formData.get("email") || "").trim();
        const password = String(formData.get("password") || "");

        if (!email || !password) {
            showAlert(els.loginAlert, "Informe email e senha.");
            return;
        }

        els.loginButton.disabled = true;
        els.loginButton.textContent = "Entrando...";

        try {
            const payload = await apiFetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });
            storeSession(payload);
            els.loginForm.reset();
            render();
        } catch (error) {
            showAlert(els.loginAlert, error.message);
        } finally {
            els.loginButton.disabled = false;
            els.loginButton.textContent = "Entrar";
        }
    }

    async function handleStockShortcut(event) {
        event.preventDefault();
        const addressText = els.stockAddressInput.value.trim();
        if (!addressText) {
            showAlert(els.dashboardAlert, "Informe o codigo do endereco para consultar saldo.");
            return;
        }

        try {
            hideAlert(els.dashboardAlert);
            const code = await resolveAddressCode(addressText);
            els.stockAddressInput.value = code;
            const payload = await apiFetch(`/api/contagens/saldo/${encodeURIComponent(code)}`);
            renderResult(els.stockResult, "Saldo por endereco", payload);
        } catch (error) {
            showAlert(els.dashboardAlert, error.message);
        }
    }

    async function handleReportShortcut(event) {
        event.preventDefault();
        const user = state.session && state.session.user;
        if (!user || user.perfil !== "gerente") {
            showAlert(els.dashboardAlert, "Relatorio disponivel apenas para gerente.");
            return;
        }

        const addressText = els.reportAddressInput.value.trim();
        if (!addressText) {
            showAlert(els.dashboardAlert, "Informe o codigo do endereco para consultar divergencia.");
            return;
        }

        try {
            hideAlert(els.dashboardAlert);
            const code = await resolveAddressCode(addressText);
            els.reportAddressInput.value = code;
            const payload = await apiFetch(`/api/relatorios/divergencia/${encodeURIComponent(code)}`);
            renderResult(els.reportResult, "Divergencia por endereco", payload);
        } catch (error) {
            showAlert(els.dashboardAlert, error.message);
        }
    }

    async function handleProductSubmit(event) {
        event.preventDefault();
        hideAlert(els.productFormAlert);
        const formData = new FormData(els.productForm);
        const payload = {
            codigo: String(formData.get("codigo") || "").trim(),
            descricao: String(formData.get("descricao") || "").trim(),
            unidade: String(formData.get("unidade") || "").trim(),
        };

        if (!payload.codigo || !payload.descricao || !payload.unidade) {
            showAlert(els.productFormAlert, "Preencha SKU, descricao e unidade.");
            return;
        }

        els.saveProductButton.disabled = true;
        try {
            await apiFetch("/api/produtos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            getModal(els.productModal).hide();
            resetForm(els.productForm, els.productFormAlert);
            await loadProducts();
        } catch (error) {
            showAlert(els.productFormAlert, error.message);
        } finally {
            els.saveProductButton.disabled = false;
        }
    }

    async function handleAddressSubmit(event) {
        event.preventDefault();
        hideAlert(els.addressFormAlert);
        const formData = new FormData(els.addressForm);
        const payload = {
            codigo: String(formData.get("codigo") || "").trim(),
            descricao: String(formData.get("descricao") || "").trim() || null,
        };

        if (!payload.codigo) {
            showAlert(els.addressFormAlert, "Preencha o codigo do endereco.");
            return;
        }

        els.saveAddressButton.disabled = true;
        try {
            await apiFetch("/api/enderecos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            getModal(els.addressModal).hide();
            resetForm(els.addressForm, els.addressFormAlert);
            await loadAddresses();
        } catch (error) {
            showAlert(els.addressFormAlert, error.message);
        } finally {
            els.saveAddressButton.disabled = false;
        }
    }

    async function handleCountSubmit(event) {
        event.preventDefault();
        hideAlert(els.countFormAlert);
        const formData = new FormData(els.countForm);
        const productText = String(formData.get("sku") || "").trim();
        const addressText = String(formData.get("codigo_endereco") || "").trim();
        const quantity = Number(formData.get("quantidade"));
        const countedAt = String(formData.get("contado_em") || "").trim();

        if (!productText || !addressText || Number.isNaN(quantity)) {
            showAlert(els.countFormAlert, "Preencha produto, endereco e quantidade.");
            return;
        }

        els.saveCountButton.disabled = true;
        try {
            const payload = {
                sku: await resolveProductCode(productText),
                codigo_endereco: await resolveAddressCode(addressText),
                quantidade: quantity,
            };
            if (countedAt) {
                payload.contado_em = countedAt;
            }

            await apiFetch("/api/contagens", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            getModal(els.countModal).hide();
            resetForm(els.countForm, els.countFormAlert);
            els.productOptions.classList.add("d-none");
            els.addressOptions.classList.add("d-none");
        } catch (error) {
            showAlert(els.countFormAlert, error.message);
        } finally {
            els.saveCountButton.disabled = false;
        }
    }

    els.loginForm.addEventListener("submit", handleLogin);
    els.logoutButton.addEventListener("click", () => {
        clearSession();
        render();
    });
    els.prevProductsButton.addEventListener("click", () => {
        state.productPage = Math.max(state.productPage - 1, 1);
        loadProducts().catch((error) => showAlert(els.dashboardAlert, error.message));
    });
    els.nextProductsButton.addEventListener("click", () => {
        state.productPage = Math.min(state.productPage + 1, state.productPages);
        loadProducts().catch((error) => showAlert(els.dashboardAlert, error.message));
    });
    els.prevAddressesButton.addEventListener("click", () => {
        state.addressPage = Math.max(state.addressPage - 1, 1);
        loadAddresses().catch((error) => showAlert(els.dashboardAlert, error.message));
    });
    els.nextAddressesButton.addEventListener("click", () => {
        state.addressPage = Math.min(state.addressPage + 1, state.addressPages);
        loadAddresses().catch((error) => showAlert(els.dashboardAlert, error.message));
    });
    els.stockShortcutForm.addEventListener("submit", handleStockShortcut);
    els.reportShortcutForm.addEventListener("submit", handleReportShortcut);
    els.productForm.addEventListener("submit", handleProductSubmit);
    els.addressForm.addEventListener("submit", handleAddressSubmit);
    els.countForm.addEventListener("submit", handleCountSubmit);
    els.countProductInput.addEventListener("input", scheduleProductSearch);
    els.countProductInput.addEventListener("focus", scheduleProductSearch);
    els.countAddressInput.addEventListener("input", () => {
        scheduleAddressSearch(els.countAddressInput, els.addressOptions, "addressSearchTimer", els.countFormAlert);
    });
    els.countAddressInput.addEventListener("focus", () => {
        scheduleAddressSearch(els.countAddressInput, els.addressOptions, "addressSearchTimer", els.countFormAlert);
    });
    els.stockAddressInput.addEventListener("input", () => {
        scheduleAddressSearch(els.stockAddressInput, els.stockAddressOptions, "stockAddressSearchTimer", els.dashboardAlert);
    });
    els.stockAddressInput.addEventListener("focus", () => {
        scheduleAddressSearch(els.stockAddressInput, els.stockAddressOptions, "stockAddressSearchTimer", els.dashboardAlert);
    });
    els.reportAddressInput.addEventListener("input", () => {
        scheduleAddressSearch(els.reportAddressInput, els.reportAddressOptions, "reportAddressSearchTimer", els.dashboardAlert);
    });
    els.reportAddressInput.addEventListener("focus", () => {
        scheduleAddressSearch(els.reportAddressInput, els.reportAddressOptions, "reportAddressSearchTimer", els.dashboardAlert);
    });
    document.addEventListener("click", (event) => {
        if (!els.countProductInput.contains(event.target) && !els.productOptions.contains(event.target)) {
            els.productOptions.classList.add("d-none");
        }
        if (!els.countAddressInput.contains(event.target) && !els.addressOptions.contains(event.target)) {
            els.addressOptions.classList.add("d-none");
        }
        if (!els.stockAddressInput.contains(event.target) && !els.stockAddressOptions.contains(event.target)) {
            els.stockAddressOptions.classList.add("d-none");
        }
        if (!els.reportAddressInput.contains(event.target) && !els.reportAddressOptions.contains(event.target)) {
            els.reportAddressOptions.classList.add("d-none");
        }
    });
    els.productModal.addEventListener("hidden.bs.modal", () => resetForm(els.productForm, els.productFormAlert));
    els.addressModal.addEventListener("hidden.bs.modal", () => resetForm(els.addressForm, els.addressFormAlert));
    els.countModal.addEventListener("hidden.bs.modal", () => {
        resetForm(els.countForm, els.countFormAlert);
        els.productOptions.classList.add("d-none");
        els.addressOptions.classList.add("d-none");
    });

    state.session = getStoredSession();
    render();
})();
