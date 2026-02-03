import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export default function ServiceorderPage() {

  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [saving, setSaving] = useState(false);

  // =============================
  // FORM DATA
  // =============================

  const [form, setForm] = useState({
    so: "",
    supplier: "",
    customer_ref: "",
    po: "",
    status: "",
    price_type: "",
    employee: "",
    remarks: "",
  });

  function updateField(name, value) {
    setForm(prev => ({ ...prev, [name]: value }));
  }

  // =============================
  // LOCK SERVICEORDER NR AFTER SAVE
  // =============================

  const [soLocked, setSoLocked] = useState(false);

  // =============================
  // CUSTOMERS + CONTACTPERSONS
  // =============================

  const [customers, setCustomers] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [email, setEmail] = useState("");

  useEffect(() => {
    async function loadCustomers() {
      try {
        const res = await axios.get(`${API}/customers`, {
          headers: { "x-api-key": "CHANGE_ME", Authorization: `Bearer ${token}` }
        });
        setCustomers(res.data);
      } catch (err) {
        console.error(err);
        toast.error("Klantgegevens laden mislukt");
      }
    }
    loadCustomers();
  }, []);

  // klant selectie → laad contactpersonen + prijstype
  useEffect(() => {

    const cust = customers.find(c => c.name === form.supplier);

    if (!cust) {
      setContacts([]);
      setEmail("");
      return;
    }

    // prijs type automatisch vullen
    if (cust.price_type) {
      updateField("price_type", cust.price_type);
    }

    // contactpersonen ophalen
    async function loadContacts() {
      try {
        const res = await axios.get(
          `${API}/customers/${cust.id}/contacts`,
          {
            headers: { "x-api-key": "CHANGE_ME", Authorization: `Bearer ${token}` }
          }
        );

        setContacts(res.data);

        const primary = res.data.find(c => c.is_primary);

        if (primary) {
          setEmail(primary.email);
        }

      } catch (err) {
        console.error(err);
      }
    }

    loadContacts();

  }, [form.supplier, customers]);

  // =============================
  // SAVE SERVICE ORDER HEADER
  // =============================

  async function handleSaveOrder() {

    if (!form.so.trim()) {
      toast.error("Serviceorder nummer verplicht");
      return;
    }

    try {
      setSaving(true);

      await axios.post(
        `${API}/serviceorders/upsert`,
        form,
        {
          headers: { "x-api-key": "CHANGE_ME", Authorization: `Bearer ${token}` }
        }
      );

      toast.success("Serviceorder opgeslagen");
      setSoLocked(true);

      await loadItems(form.so);

    } catch (err) {
      console.error(err);
      toast.error("Opslaan mislukt");
    } finally {
      setSaving(false);
    }
  }

  // =============================
  // ORDER ITEMS
  // =============================

  const [items, setItems] = useState([]);

  async function loadItems(so) {
    try {
      const res = await axios.get(
        `${API}/serviceorders/${so}/items`,
        {
          headers: { "x-api-key": "CHANGE_ME", Authorization: `Bearer ${token}` }
        }
      );
      setItems(res.data);
    } catch (err) {
      console.error(err);
    }
  }

  // =============================
  // ADD ARTICLE BY PART NUMBER
  // =============================

  const [newPartNo, setNewPartNo] = useState("");

  async function addArticleByPartNo() {

    if (!soLocked) {
      toast.error("Sla eerst de serviceorder op");
      return;
    }

    if (!newPartNo.trim()) return;

    try {
      const res = await axios.get(
        `${API}/articles/${newPartNo}`,
        {
          headers: { "x-api-key": "CHANGE_ME", Authorization: `Bearer ${token}` }
        }
      );

      const art = res.data;

      setItems(prev => [
        ...prev,
        {
          part_no: art.part_no,
          description: art.description || "",
          qty: 1,
          list_price: art.list_price || 0,
          price_bruto: art.price_bruto || 0,
          price_wvk: art.price_wvk || 0,
          price_edmac: art.price_edmac || 0,
          bestellen: false
        }
      ]);

      setNewPartNo("");

    } catch (err) {
      console.error(err);
      toast.error("Artikel niet gevonden");
    }
  }

  function updateItem(index, field, value) {
    setItems(prev => {
      const arr = [...prev];
      arr[index] = { ...arr[index], [field]: value };
      return arr;
    });
  }

  function deleteItem(index) {
    setItems(prev => prev.filter((_, i) => i !== index));
  }

  async function saveItems() {
    try {
      await axios.post(
        `${API}/serviceorders/${form.so}/items/replace`,
        items,
        {
          headers: { "x-api-key": "CHANGE_ME", Authorization: `Bearer ${token}` }
        }
      );
      toast.success("Artikelen opgeslagen");
    } catch (err) {
      console.error(err);
      toast.error("Opslaan artikelen mislukt");
    }
  }

  // =============================
  // UI
  // =============================

  return (
    <div className="min-h-screen bg-gray-100 p-8">

      <h1 className="text-2xl font-bold mb-6">Serviceorder</h1>

      <div className="bg-white rounded-2xl shadow p-6 space-y-6">

        {/* SERVICEORDER HEADER */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

          <div>
            <label>Serviceorder *</label>
            <input
              className="w-full border rounded px-3 py-2"
              disabled={soLocked}
              value={form.so}
              onChange={e => updateField("so", e.target.value)}
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

          <div>
            <label>Prijs type</label>
            <input
              className="w-full border rounded px-3 py-2 bg-gray-100"
              disabled
              value={form.price_type}
            />
          </div>

        </div>

        {/* CUSTOMER SECTION */}

        <h2 className="font-semibold mt-4">Klant</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          <div>
            <label>Klant</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={form.supplier}
              onChange={e => updateField("supplier", e.target.value)}
            >
              <option value="">-- kies klant --</option>

              {customers.map(c => (
                <option key={c.id} value={c.name}>
                  {c.name}
                </option>
              ))}

            </select>
          </div>

          <div>
            <label>Email</label>
            <input
              className="w-full border rounded px-3 py-2 bg-gray-100"
              disabled
              value={email}
            />
          </div>

        </div>

        <button
          onClick={handleSaveOrder}
          className="px-6 py-2 bg-green-600 text-white rounded"
        >
          Serviceorder opslaan
        </button>

        {/* =============================
            ITEMS SECTION
        ============================= */}

        {soLocked && (
          <>
            <h2 className="text-xl font-bold mt-6">Artikelen</h2>

            <div className="flex gap-2">
              <input
                className="border rounded px-3 py-2"
                value={newPartNo}
                placeholder="Part no"
                onChange={e => setNewPartNo(e.target.value)}
              />

              <button
                className="px-4 py-2 bg-blue-600 text-white rounded"
                onClick={addArticleByPartNo}
              >
                Toevoegen
              </button>
            </div>

            <table className="w-full mt-4 text-sm border">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2">Part no</th>
                  <th className="border p-2">Omschrijving</th>
                  <th className="border p-2">Aantal</th>
                  <th className="border p-2">LIST</th>
                  <th className="border p-2">BRUTO</th>
                  <th className="border p-2">WVK</th>
                  <th className="border p-2">EDMAC</th>
                  <th className="border p-2">X</th>
                </tr>
              </thead>

              <tbody>
                {items.map((it, idx) => (
                  <tr key={idx}>
                    <td className="border p-1">{it.part_no}</td>
                    <td className="border p-1">{it.description}</td>

                    <td className="border p-1">
                      <input
                        type="number"
                        className="w-full"
                        value={it.qty}
                        onChange={e =>
                          updateItem(idx, "qty", Number(e.target.value))
                        }
                      />
                    </td>

                    <td className="border p-1">{it.list_price}</td>
                    <td className="border p-1">{it.price_bruto}</td>
                    <td className="border p-1">{it.price_wvk}</td>
                    <td className="border p-1">{it.price_edmac}</td>

                    <td className="border p-1 text-center">
                      <button
                        className="text-red-600"
                        onClick={() => deleteItem(idx)}
                      >
                        ✖
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <button
              onClick={saveItems}
              className="mt-3 px-6 py-2 bg-green-700 text-white rounded"
            >
              Artikelen opslaan
            </button>
          </>
        )}

      </div>
    </div>
  );
}
