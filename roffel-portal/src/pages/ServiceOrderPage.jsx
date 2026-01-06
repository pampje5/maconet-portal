import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export default function ServiceorderPage() {

  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [form, setForm] = useState({
    so: "",
    customer_ref: "",
    po: "",
    status: "",
    supplier: "",
    price_type: "",
    remarks: "",
  });

  // ========================
  // TIJDELIJKE CONTACTGEGEVENS SULLAIR
  // ========================
  const SULLAIR_CONTACT_NAME = "John Doe";
  const SULLAIR_CONTACT_EMAIL = "orders@sullair.com";


  function updateField(name, value) {
    setForm(prev => ({ ...prev, [name]: value }));
  }

  const [soLocked, setSoLocked] = useState(false);

  // ============================
  // CUSTOMERS + CONTACTEN
  // ============================

  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);

  const [contacts, setContacts] = useState([]);
  const [selectedContactId, setSelectedContactId] = useState(null);

  useEffect(() => {
    async function loadCustomers() {
      try {
        const res = await axios.get(`${API}/customers`, {
          headers: {
            "x-api-key": "CHANGE_ME",
            Authorization: `Bearer ${token}`,
          },
        });

        setCustomers(res.data);
      } catch (err) {
        console.error(err);
        toast.error("Kon klanten niet laden");
      }
    }

    loadCustomers();
  }, []);

  // klant gekozen → prijs_type + contacten ophalen
  useEffect(() => {
    if (!selectedCustomerId) {
      setContacts([]);
      updateField("price_type", "");
      return;
    }

    const cust = customers.find(c => c.id === selectedCustomerId);

    if (cust) {
      // customer name in form.supplier
      updateField("supplier", cust.name);
      // PRIJSTYPE HIER INVULLEN
      updateField("price_type", cust.price_type || "");
    }

    async function loadContacts() {
      try {
        const res = await axios.get(
          `${API}/customers/${selectedCustomerId}/contacts`,
          {
            headers: {
              "x-api-key": "CHANGE_ME",
              Authorization: `Bearer ${token}`,
            }
          }
        );

        setContacts(res.data);

        const primary = res.data.find(c => c.is_primary);

        if (primary) {
          setSelectedContactId(primary.id);
        }

      } catch (err) {
        console.error(err);
      }
    }

    loadContacts();

  }, [selectedCustomerId, customers]);


  // ============================
  // OPSLAAN SERVICEORDER
  // ============================

  async function saveOrder() {

    if (!form.so.trim()) {
      alert("Serviceorder nummer is verplicht");
      return;
    }

    try {
      await axios.post(
        `${API}/serviceorders/upsert`,
        form,
        {
          headers: {
            "x-api-key": "CHANGE_ME",
            Authorization: `Bearer ${token}`,
          }
        }
      );

      toast.success("Serviceorder opgeslagen");
      setSoLocked(true);

    } catch (err) {
      console.error(err);
      toast.error("Opslaan mislukt");
    }
  }

  // ============================
  // ARTIKELEN
  // ============================

  const [items, setItems] = useState([]);
  const [newPartNo, setNewPartNo] = useState("");

  async function addArticle() {

    if (!newPartNo.trim()) return;

    try {
      const res = await axios.get(
        `${API}/articles/${newPartNo}`,
        {
          headers: {
            "x-api-key": "CHANGE_ME",
            Authorization: `Bearer ${token}`
          }
        }
      );

      const a = res.data;

      setItems(prev => [
        ...prev,
        {
          part_no: a.part_no,
          description: a.description,
          qty: 1,
          price_bruto: a.price_bruto,
          price_wvk: a.price_wvk,
          price_edmac: a.price_edmac,
          bestellen: false
        }
      ]);

      setNewPartNo("");

    } catch (err) {
      toast.error("Artikel niet gevonden");
    }
  }

  async function saveItems() {

    await axios.post(
      `${API}/serviceorders/${form.so}/items/replace`,
      items,
      {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`
        }
      }
    );

    toast.success("Artikelen opgeslagen");
  }

  // ============================
  // MAIL SULLAIR
  // ============================

  function prepareSullairRequestEmail() {

  if (!form.so) {
    alert("Geen serviceorder nummer ingevuld");
    return;
  }

  if (!items.length) {
    alert("Geen artikelen ingevoerd");
    return;
  }

  // HTML tabelregels opbouwen
  const rows = items
    .map((it, idx) => `
      <tr>
        <td style="border:1px solid #000;padding:4px;text-align:center;">${idx + 1}</td>
        <td style="border:1px solid #000;padding:4px;">${it.part_no}</td>
        <td style="border:1px solid #000;padding:4px;">${it.description || ""}</td>
        <td style="border:1px solid #000;padding:4px;text-align:center;">${it.qty}</td>
        <td style="border:1px solid #000;padding:4px;text-align:right;">${it.price_bruto ?? ""}</td>
        <td style="border:1px solid #000;padding:4px;"></td>
        <td style="border:1px solid #000;padding:4px;"></td>
      </tr>
    `)
    .join("");

  const htmlBody = `
Dear ${SULLAIR_CONTACT_NAME},<br><br>

We kindly request, with SO no.: <b>${form.so}</b>, the leadtimes for the following items:<br><br>

<table style="border-collapse:collapse;">
  <tr>
    <th style="border:1px solid #000;padding:4px;">Item</th>
    <th style="border:1px solid #000;padding:4px;">Part No.</th>
    <th style="border:1px solid #000;padding:4px;">Description</th>
    <th style="border:1px solid #000;padding:4px;">QTY</th>
    <th style="border:1px solid #000;padding:4px;">Price Each</th>
    <th style="border:1px solid #000;padding:4px;">Leadtime NL</th>
    <th style="border:1px solid #000;padding:4px;">Comments</th>
  </tr>
  ${rows}
</table>

<br>
Kind regards,<br><br>
Maconet B.V.
`;

  const subject = `Leadtime request service order ${form.so}`;

  const mailto =
    `mailto:${SULLAIR_CONTACT_EMAIL}` +
    `?subject=${encodeURIComponent(subject)}` +
    `&body=${encodeURIComponent(htmlBody)}`;

  window.location.href = mailto;
}

function generateSullairRequestEML() {

  if (!form.so) {
    alert("Geen serviceorder ingevuld");
    return;
  }

  if (!items.length) {
    alert("Geen artikelen in de serviceorder");
    return;
  }

  const sullairEmail = "orders@sullair.com";
  const sullairName = "John Doe";

  // HTML BODY
  const htmlBody = `
<html>
<body>
Dear ${sullairName},<br><br>

We kindly request, with SO no.: <b>${form.so}</b>, the leadtimes for the following items:<br><br>

<table style="border-collapse:collapse;">
<tr>
<th style="border:1px solid #000;padding:4px;">Item</th>
<th style="border:1px solid #000;padding:4px;">Part No.</th>
<th style="border:1px solid #000;padding:4px;">Description</th>
<th style="border:1px solid #000;padding:4px;">QTY</th>
<th style="border:1px solid #000;padding:4px;">Price Each</th>
<th style="border:1px solid #000;padding:4px;">Leadtime NL</th>
<th style="border:1px solid #000;padding:4px;">Comments</th>
</tr>

${items.map((it, idx) => `
<tr>
<td style="border:1px solid #000;padding:4px;text-align:center;">${idx + 1}</td>
<td style="border:1px solid #000;padding:4px;">${it.part_no}</td>
<td style="border:1px solid #000;padding:4px;">${it.description || ""}</td>
<td style="border:1px solid #000;padding:4px;text-align:center;">${it.qty}</td>
<td style="border:1px solid #000;padding:4px;text-align:right;">${it.price_bruto || ""}</td>
<td style="border:1px solid #000;padding:4px;"></td>
<td style="border:1px solid #000;padding:4px;"></td>
</tr>
`).join("")}

</table>

<br>
Kind regards,<br><br>

Maconet B.V.<br>

</body>
</html>
  `;

  // required CRLF
  function crlf(str) {
    return str.replace(/\n/g, "\r\n");
  }

  // EML STRUCTURE — Outlook Friendly
  const eml =
`To: ${sullairEmail}
From: Maconet B.V. <no-reply@maconet.local>
Subject: Leadtime request service order ${form.so}
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8
Date: ${new Date().toUTCString()}

${htmlBody}`;

  const blob = new Blob([crlf(eml)], { type: "message/rfc822" });

  // 👉 On Windows + Outlook this OPENS a draft email
  const url = URL.createObjectURL(blob);
  window.location.href = url;

  setTimeout(() => URL.revokeObjectURL(url), 2000);
}



  // ============================
  // UI
  // ============================

  return (
    <div className="min-h-screen bg-gray-100 p-8">

      <h1 className="text-2xl font-bold mb-6">
        Serviceorder Sullair
      </h1>

      <div className="bg-white rounded-2xl shadow p-6 space-y-8">

        {/* SERVICEORDER BLOK */}
        <div>
          <h2 className="font-semibold mb-2">Serviceorder *</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div>
              <label>Serviceorder nr *</label>
              <input
                className="w-full border rounded px-3 py-2"
                disabled={soLocked}
                value={form.so}
                onChange={e => updateField("so", e.target.value)}
              />
            </div>

            <div>
              <label>Klantreferentie</label>
              <input
                className="w-full border rounded px-3 py-2"
                value={form.customer_ref}
                onChange={e => updateField("customer_ref", e.target.value)}
              />
            </div>

            <div>
              <label>Inkoopnummer (PO)</label>
              <input
                className="w-full border rounded px-3 py-2"
                value={form.po}
                onChange={e => updateField("po", e.target.value)}
              />
            </div>

            <div>
              <label>Status</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={form.status}
                onChange={e => updateField("status", e.target.value)}
              >
                <option value="">-- kies status --</option>
                <option>OPEN</option>
                <option>AANGEVRAAGD</option>
                <option>OFFERTE</option>
                <option>BESTELD</option>
                <option>ONTVANGEN</option>
                <option>AFGEHANDELD</option>
              </select>
            </div>

          </div>
        </div>

        {/* KLANT BLOK */}
        <div>
          <h2 className="font-semibold mb-2">Klant</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div>
              <label>Klant</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={selectedCustomerId || ""}
                onChange={e => setSelectedCustomerId(Number(e.target.value))}
              >
                <option value="">-- kies klant --</option>

                {customers.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Contactpersoon</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={selectedContactId || ""}
                onChange={e => setSelectedContactId(Number(e.target.value))}
              >
                <option value="">-- kies contactpersoon --</option>

                {contacts.map(ct => (
                  <option key={ct.id} value={ct.id}>
                    {ct.contact_name} — {ct.email} {ct.is_primary ? "(primair)" : ""}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Prijstype</label>
              <input
                className="w-full border rounded px-3 py-2 bg-gray-100"
                disabled
                value={form.price_type}
              />
            </div>

          </div>
        </div>

        <button
          className="bg-green-600 text-white px-6 py-2 rounded"
          onClick={saveOrder}
        >
          Serviceorder opslaan
        </button>

        {/* ARTIKELEN */}
        {soLocked && (
          <div>
            <h2 className="font-semibold mt-6">Artikelen</h2>

            <div className="flex gap-2 mt-2">
              <input
                className="border rounded px-3 py-2"
                placeholder="Part nr"
                value={newPartNo}
                onChange={e => setNewPartNo(e.target.value)}
              />

              <button
                className="bg-blue-600 text-white px-4 py-2 rounded"
                onClick={addArticle}
              >
                Toevoegen
              </button>
            </div>

            <table className="w-full mt-3 border text-sm">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2">Part nr</th>
                  <th className="border p-2">Omschrijving</th>
                  <th className="border p-2">Aantal</th>
                  <th className="border p-2">Bruto</th>
                  <th className="border p-2">WVK</th>
                  <th className="border p-2">Edmac</th>
                </tr>
              </thead>

              <tbody>
                {items.map((it, i) => (
                  <tr key={i}>
                    <td className="border p-1">{it.part_no}</td>
                    <td className="border p-1">{it.description}</td>

                    <td className="border p-1">
                      <input
                        type="number"
                        value={it.qty}
                        onChange={e => {
                          const qty = Number(e.target.value);
                          setItems(prev => {
                            const cp = [...prev];
                            cp[i].qty = qty;
                            return cp;
                          });
                        }}
                      />
                    </td>

                    <td className="border p-1">{it.price_bruto}</td>
                    <td className="border p-1">{it.price_wvk}</td>
                    <td className="border p-1">{it.price_edmac}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <button
              className="bg-green-700 text-white px-5 py-2 mt-2 rounded"
              onClick={saveItems}
            >
              Artikelen opslaan
            </button>

            <button
              className="mt-3 px-6 py-2 bg-blue-700 text-white rounded"
              onClick={prepareSullairRequestEmail}
            >
              Aanvraag bij Sullair voorbereiden
            </button>

            <button
              onClick={generateSullairRequestEML}
              className="mt-3 px-6 py-2 bg-purple-700 text-white rounded"
            >
              Aanvraag Sullair (leadtime)
            </button>


          </div>
        )}

      </div>
    </div>
  );
}
