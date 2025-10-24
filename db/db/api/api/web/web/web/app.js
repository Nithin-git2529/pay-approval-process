const API = "http://127.0.0.1:5000";

async function submitRequest() {
  const employee_id = Number(document.getElementById("empId").value);
  const amount = Number(document.getElementById("amount").value);
  const reason = document.getElementById("reason").value;
  const msg = document.getElementById("submitMsg");

  try {
    const res = await fetch(`${API}/request`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ employee_id, amount, reason })
    });
    const data = await res.json();
    msg.textContent = `Created request #${data.request_id}`;
    loadRequests();
  } catch (e) {
    msg.textContent = "Failed to submit";
  }
}

async function loadRequests() {
  const out = document.getElementById("requests");
  const res = await fetch(`${API}/requests`);
  const data = await res.json();
  out.textContent = JSON.stringify(data, null, 2);
}

async function approve() {
  const request_id = Number(document.getElementById("reqId").value);
  const manager_id = Number(document.getElementById("mgrId").value);
  await fetch(`${API}/approve`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ request_id, manager_id })
  });
  loadRequests();
}

async function reject() {
  const request_id = Number(document.getElementById("reqId").value);
  const manager_id = Number(document.getElementById("mgrId").value);
  const reason = document.getElementById("rejReason").value;
  await fetch(`${API}/reject`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ request_id, manager_id, reason })
  });
  loadRequests();
}

loadRequests();
