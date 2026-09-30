async function api(path, options = {}) {
    options.headers = options.headers || {};

    const token = localStorage.getItem("token");

    if (token) {
        options.headers.Authorization =
            `Bearer ${token}`;
    }

    const response = await fetch(
        path,
        options
    );

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (response.status === 401) {
        localStorage.removeItem("token");

        if (
            !location.pathname.includes("/login") &&
            !location.pathname.includes("/register")
        ) {
            location = "/login";
        }
    }

    return data;
}


function escapeHtml(value) {
    return String(value).replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]
    );
}


function render(data) {

    const element =
        document.querySelector("#results");

    if (!element) {
        return;
    }

    if (data.detail) {
        element.innerHTML =
            `<div class="error">
                ${escapeHtml(data.detail)}
            </div>`;

        return;
    }

    const rows =
        (data.recommendations || [])
            .map(item => `
                <article class="rec-card">

                    <div>
                        <span class="pill">
                            ${escapeHtml(item.platform)}
                        </span>

                        <h3>
                            ${escapeHtml(item.title)}
                        </h3>

                        <p>
                            ${escapeHtml(item.reason)}
                        </p>
                    </div>

                    <strong>
                        ₹${(
                            item.price *
                            item.quantity
                        ).toLocaleString()}
                    </strong>

                    <a
                        href="${escapeHtml(item.url)}"
                        target="_blank"
                        rel="noopener"
                    >
                        Search platform ↗
                    </a>

                </article>
            `)
            .join("");


    element.innerHTML = `
        <div class="summary">

            <b>
                ${escapeHtml(
                    data.summary ||
                    "Plan ready"
                )}
            </b>

            <span>
                Allocated ₹${Number(
                    data.allocated_total
                ).toLocaleString()}

                · Remaining ₹${Number(
                    data.remaining_budget
                ).toLocaleString()}
            </span>

            ${
                data.image_insight
                    ? `
                        <small>
                            ${escapeHtml(
                                data.image_insight
                            )}
                        </small>
                    `
                    : ""
            }

        </div>

        ${
            rows ||
            "<p>No recommendations fit the budget.</p>"
        }
    `;
}


function logout() {
    localStorage.removeItem("token");
    location = "/login";
}


(function () {

    const authLink =
        document.querySelector("#authLink");

    if (
        authLink &&
        localStorage.token
    ) {
        authLink.textContent =
            "Dashboard";

        authLink.href =
            "/dashboard";
    }

})();