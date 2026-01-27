import { useState, useEffect, useMemo, useRef } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import { formatCurrency, formatQty } from "../utils/format";
import { useSearchParams, useNavigate } from "react-router-dom";
import ActionBar from "../components/ActionBar";
import Button from "../components/ui/Button";
import ConfirmLeaveModal from "../components/ConfirmLeaveModal";
import { useNavigationGuard } from "../context/NavigationGuardContext";


export default function ServiceorderPage() {
  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [searchParams] = useSearchParams();
  const soFromUrl = searchParams.get("so"); // string | null

  const [form, setForm] = useState({
    so: "",
    customer_id: null,
    supplier_id: 2,   // default
    customer_ref: "",
    po: "",
    status: "",
    price_type: "",
    remarks: "",
  });

  const [soReserved, setSoReserved] = useState(false);

  const [soLocked, setSoLocked] = useState(false);

  // ========================
  // Mail preview modal
  // ========================
  const [mailPreview, setMailPreview] = useState({
    to: "",
    subject: "",
    body_html: "",
    // pdf kan erbij komen vanuit backend (stock order preview)
  });
  const [showMailModal, setShowMailModal] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // =========================
  // Leave Modal
  // =========================
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const navigate = useNavigate();
  const [pendingNavigation, setPendingNavigation] = useState(null);

  // =========================
  // Customers + contacts + suppliers
  // =========================
  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);

  const [contacts, setContacts] = useState([]);
  const [selectedContactId, setSelectedContactId] = useState(null);

  const [suppliers, setSuppliers] = useState([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState(null);

  // ========================
  // Status
  // ========================
  const [allowedStatuses, setAllowedStatuses] = useState([]);


  // =========================
  // Items
  // =========================
  const [items, setItems] = useState([]);
  const [newPartNo, setNewPartNo] = useState("");

  // =========================
  // Loading states
  // =========================
  const [loadingOrder, setLoadingOrder] = useState(false);
  const [loadingItems, setLoadingItems] = useState(false);

  function updateField(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  const [log, setLog] = useState([]);

  // =========================
  // Saving guard
  // =========================
  const isSavingRef = useRef(false);

  const { registerBlocker } = useNavigationGuard();

  useEffect(() => {
    const dirty = form.so && !soLocked; // jouw logica
    registerBlocker(dirty, (to) => {
      setPendingNavigation(to);
      setShowLeaveModal(true);
    });

    return () => registerBlocker(false, null); // opruimen bij unmount
  }, [form.so, soLocked]);


  // =========================
  // Unknown article modal
  // =========================
  const [showUnknownArticleModal, setShowUnknownArticleModal] = useState(false);
  const [unknownPartNo, setUnknownPartNo] = useState("");

  // =========================
  // Pakbon modal
  // =========================
  const [showPackingSlipModal, setShowPackingSlipModal] = useState(false);
  const [packingSlipOptions, setPackingSlipOptions] = useState({
    customer: false,
    internal: false,
  });

  
  // =======================
  // Helpers
  // =======================
  

  const hasReceivedItems = useMemo(
    () => items.some((it) => it.ontvangen === true),
    [items]
  );

  const hasOrderedItems = useMemo(
    () => items.some((it) => it.bestellen === true),
    [items]
  );

  const hasPackingSlipSelection =
    packingSlipOptions.customer || packingSlipOptions.internal;

  const hasUnsavedSO = Boolean(form.so && !soLocked);


  // =========================
  // Serviceordernr
  // =========================
  async function reserveServiceOrderNumber() {
    try {
      const res = await axios.post(
        `${API}/serviceorder-numbers/reserve`,
        null,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      updateField("so", res.data.so_number);
      setSoReserved(true);

      toast.success(`Serviceordernummer ${res.data.so_number} gereserveerd`);
    } catch (err) {
      console.error(err);
      toast.error("Kon serviceordernummer niet reserveren");
    }
  }

  // =========================
  // Load suppliers
  // =========================

  useEffect(() => {
  async function loadSuppliers() {
    try {
      const res = await axios.get(`${API}/suppliers`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const activeSuppliers = res.data.filter(s => s.is_active);
      setSuppliers(activeSuppliers);

      // default: Sullair (optioneel maar handig)
      const sullair = res.data.find(s => s.name === "Sullair");
      if (sullair) setSelectedSupplierId(sullair.id);
    } catch (err) {
      console.error(err);
      toast.error("Kon leveranciers niet laden");
    }
  }

  if (token) loadSuppliers();
}, [API, token]);


  // =========================
  // Load customers
  // =========================
  useEffect(() => {
    async function loadCustomers() {
      try {
        const res = await axios.get(`${API}/customers`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setCustomers(res.data);
      } catch (err) {
        console.error(err);
        toast.error("Kon klanten niet laden");
      }
    }

    if (token) loadCustomers();
  }, [API, token]);


  // =========================
  // Load status
  // =========================
  useEffect(() => {
    if (form.so) {
      loadAllowedStatuses(form.so);
    }
  }, [form.so]);




  // =========================
  // When customer selected -> set customer_id + price_type + load contacts
  // =========================
 useEffect(() => {
  async function loadContacts(customerId) {
    try {
      const res = await axios.get(
        `${API}/customers/${customerId}/contacts`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setContacts(res.data);

      // default: primary contact
      const primary = res.data.find((c) => c.is_primary);
      if (primary) setSelectedContactId(primary.id);
    } catch (err) {
      console.error(err);
    }
  }

  if (!selectedCustomerId) {
    setContacts([]);
    setSelectedContactId(null);

    updateField("customer_id", null);
    updateField("price_type", "");

    return;
  }

  const cust = customers.find((c) => c.id === selectedCustomerId);
  if (cust) {
    updateField("customer_id", cust.id);
    updateField("price_type", cust.price_type || "");

    // 🔒 supplier is vast: Sullair (id = 2)
    updateField("supplier_id", 2);

    loadContacts(cust.id);
  }
}, [selectedCustomerId, customers, token, API]);

  // =========================
  // Status
  // =========================
  async function loadAllowedStatuses(so) {
  try {
    const res = await axios.get(
      `${API}/serviceorders/${so}/allowed-statuses`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    setAllowedStatuses(res.data.allowed || []);
  } catch (err) {
    console.error(err);
    toast.error("Kon statusopties niet laden");
  }
}

async function changeStatus(nextStatus) {
  if (!nextStatus || !form.so) return;

  try {
    await axios.post(
      `${API}/serviceorders/${form.so}/transition`,
      { to: nextStatus },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    // 🔄 lokale status bijwerken
    updateField("status", nextStatus);

    // 🔁 nieuwe allowed transitions ophalen
    await loadAllowedStatuses(form.so);

    toast.success(`Status gewijzigd naar ${nextStatus}`);
  } catch (err) {
    console.error(err);
    toast.error(
      err.response?.data?.detail || "Status wijzigen mislukt"
    );
  }
}


  // =========================
  // Load a single service order (from url)
  // =========================
  async function loadServiceOrder(so) {
    setLoadingOrder(true);
    try {
      const res = await axios.get(
        `${API}/serviceorders/${encodeURIComponent(so)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const order = res.data;

      setForm({
        so: order.so || "",

        customer_id: order.customer_id || null,
        supplier_id: order.supplier_id || 2, // fallback: Sullair

        customer_ref: order.customer_ref || "",
        po: order.po || "",
        status: order.status || "",
        price_type: order.price_type || "",
        remarks: order.remarks || "",
      });

      setSoLocked(true);

      if (order.customer_id) { setSelectedCustomerId(order.customer_id)};

    } catch (err) {
      console.error(err);
      toast.error("Serviceorder kon niet worden geladen");
    } finally {
      setLoadingOrder(false);
    }
  }

  async function loadItems(so) {
    setLoadingItems(true);
    try {
      const res = await axios.get(
        `${API}/serviceorders/${encodeURIComponent(so)}/items`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setItems(res.data || []);
    } catch (err) {
      console.error(err);
      toast.error("Artikelen konden niet worden geladen");
    } finally {
      setLoadingItems(false);
    }
  }

  // Trigger load when soFromUrl is present
  useEffect(() => {
    if (!soFromUrl) return;
    if (!token) return;

    // load order + items
    loadServiceOrder(soFromUrl);
    loadItems(soFromUrl);
    loadLog(soFromUrl);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [soFromUrl, token]);

  
  // =========================
  // mark received item
  // =========================
  async function markItemReceived(item) {
    try {
      await axios.post(
        `${API}/serviceorders/${form.so}/items/${item.id}/receive`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      toast.success(`Artikel ${item.part_no} ontvangen`);
      loadItems(form.so);
      loadLog(form.so);
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || "Ontvangen mislukt");
    }
  }

  // =========================
  // Save service order
  // =========================

  async function saveOrder() {
    if (!form.so) {
      toast.error("Geen serviceordernummer");
      return;
    }

    try {
      // 1️⃣ ServiceOrder opslaan (leidend)
      await axios.post(
        `${API}/serviceorders/upsert`,
        {
          ...form,
          customer_id: selectedCustomerId,
          supplier_id: selectedSupplierId,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // 2️⃣ ServiceOrderNumber details zetten (RESERVED → update toegestaan)
      await axios.put(
        `${API}/serviceorder-numbers/${form.so}`,
        buildServiceOrderNumberUpdatePayload(),
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // 3️⃣ Nummer bevestigen (body is zinloos bij jouw backend)
      await axios.post(
        `${API}/serviceorder-numbers/${form.so}/confirm`,
        null,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSoLocked(true);
      toast.success("Serviceorder opgeslagen");
    } catch (err) {
      console.error(err);
      toast.error("Opslaan mislukt");
    }
  }



  // =========================
  // Add article
  // =========================
  async function addArticle() {
    if (!newPartNo.trim()) return;

    try {
      const res = await axios.get(`${API}/articles/${newPartNo}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const a = res.data;

      setItems((prev) => [
        ...prev,
        {
          part_no: a.part_no,
          description: a.description,
          qty: 1,

          list_price: a.list_price,
          price_bruto: a.price_bruto,
          price_wvk: a.price_wvk,
          price_edmac: a.price_edmac,
          price_purchase: a.price_purchase,

          bestellen: false,
        },
      ]);

      setNewPartNo("");
    } catch (err) {
      if (err.response?.status === 404) {
        setUnknownPartNo(newPartNo);
        setShowUnknownArticleModal(true);
      } else {
        console.error(err);
        toast.error("Artikel niet gevonden");
      }
    }
  }

  function addUnknownArticle() {
    setItems((prev) => [
      ...prev,
      {
        part_no: unknownPartNo,
        description: "PART. NO. Unknown. Requested info from supplier",
        qty: 1,

        list_price: null,
        price_bruto: null,
        price_wvk: null,
        price_edmac: null,
        price_purchase: null,

        bestellen: true,
        ontvangen: false,
      },
    ]);

    setNewPartNo("");
    setUnknownPartNo("");
    setShowUnknownArticleModal(false);
  }

  async function saveItems() {
    if (!form.so) {
      toast.error("Geen serviceorder nummer");
      return;
    }

    await axios.post(`${API}/serviceorders/${form.so}/items/replace`, items, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    await loadItems(form.so);

    toast.success("Artikelen opgeslagen");
  }

  // =========================
  // Mail previews
  // =========================
  async function openSullairMailPreview() {
    if (!form.so) {
      alert("Geen serviceorder nummer");
      return;
    }

    try {
      const res = await axios.post(
        `${API}/serviceorders/${form.so}/mail/leadtime/preview`,
        null,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMailPreview(res.data);
      setEditMode(false);
      setShowMailModal(true);
      loadLog(form.so);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Fout bij ophalen mail preview");
    }
  }

  async function openOfferPreview() {
    if (!form.so) {
      alert("Geen serviceorder nummer");
      return;
    }

    try {
      const res = await axios.post(
        `${API}/serviceorders/${form.so}/mail/offer/preview`,
        null,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMailPreview(res.data);
      setEditMode(false);
      setShowMailModal(true);
      loadLog(form.so);
    } catch (err) {
      console.error(err);
      alert("Offerte preview mislukt");
    }
  }

 async function openStockOrderPreview() {
  if (!form.so) {
    toast.error("Geen serviceorder nummer");
    return;
  }

  try {
    const res = await axios.get(
      `${API}/serviceorders/${encodeURIComponent(form.so)}/order/preview`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setMailPreview(res.data);     // bevat to/subject/body_html + pdf/pdf_path (of straks pdf_url)
    setEditMode(false);
    setShowMailModal(true);
    loadLog(form.so);
  } catch (err) {
    console.error(err);
    toast.error(err.response?.data?.detail || "Stock order preview mislukt");
  }
}




  async function openOrderConfirmationPreview() {
    try {
      const res = await axios.post(
        `${API}/serviceorders/${form.so}/mail/order-confirmation/preview`,
        null,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMailPreview(res.data);
      setShowMailModal(true);
      loadLog(form.so);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Kon bestelbevestiging niet maken");
    }
  }

  async function sendMail() {
    if (!mailPreview) return;

    const isStockOrder = !!mailPreview.pdf;

    const url = isStockOrder ? `${API}/mail/stock-order/simulate` : `${API}/mail/send`;

    const payload = isStockOrder
      ? { so: form.so }
      : {
          to: mailPreview.to,
          subject: mailPreview.subject,
          body_html: mailPreview.body_html,
        };

    try {
      await axios.post(url, payload, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setShowMailModal(false);
      alert("Mail verzonden ✔");
    } catch (err) {
      console.error(err);
      alert("Verzenden mislukt ❌");
    }
  }

  async function loadLog(so) {
    try {
      const res = await axios.get(`${API}/serviceorders/${so}/log`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setLog(res.data);
    } catch (err) {
      console.error("Log ophalen mislukt", err);
    }
  }

 async function openPdfPreview() {
  if (!form.so) {
    toast.error("Geen serviceorder nummer");
    return;
  }

  try {
    const res = await fetch(
      `${API}/serviceorders/${encodeURIComponent(form.so)}/order/pdf`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!res.ok) {
      throw new Error("PDF preview mislukt");
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    window.open(url, "_blank");
  } catch (err) {
    console.error(err);
    toast.error("Kon PDF niet openen");
  }
}



  async function openPackingSlip(mode) {
    try {
      const res = await fetch(`${API}/serviceorders/${form.so}/packing-slip/${mode}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Pakbon ophalen mislukt");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");
    } catch (err) {
      console.error(err);
      toast.error("Kon pakbon niet openen");
    }
  }

  function previewPackingSlip() {
    if (packingSlipOptions.customer) {
      openPackingSlip("customer");
    }
    if (packingSlipOptions.internal) {
      openPackingSlip("internal");
    }
  }

  // Afdrukken = preview openen (gebruiker drukt zelf af)
  function printPackingSlip() {
    previewPackingSlip();
  }

  // ========================
  // Payload voor SOnmbr
  // ========================
  function buildServiceOrderNumberUpdatePayload() {
    const customer = customers.find(c => c.id === selectedCustomerId);
    const supplier = suppliers.find(s => s.id === selectedSupplierId);

    return {
      customer_id: selectedCustomerId ?? null,
      supplier_id: selectedSupplierId ?? null,

      // 👇 expliciet vullen voor weergave / historie
      customer_name_free: customer?.name ?? null,
      supplier_name_free: supplier?.name ?? null,

      description: `Sullair onderdelen, klantreferentie ${form.customer_ref || "-"}`,
      type: "VO",
    };
  }



  // ========================
  // Vrijgeven serviceordernummer na Cancel
  // ========================

  // useEffect(() => {
  //  return () => {
  //    if (form.so && !soLocked && !isSavingRef.current) {
  //      axios.post(
  //        `${API}/serviceorder-numbers/${form.so}/cancel`,
  //        null,
  //        {
  //          headers: {
  //            Authorization: `Bearer ${token}`,
  //          },
  //        }
  //      );
  //    }
  //  };
  //}, [form.so, soLocked, API, token]);

  // =========================
  // UI
  // =========================
  return (
    <>
    <ConfirmLeaveModal
        open={showLeaveModal}
        onClose={() => setShowLeaveModal(false)}
        onSave={async () => {
          await saveOrder();
          registerBlocker(false, null)
          setShowLeaveModal(false);
          navigate(pendingNavigation);
        }}
        onCancel={async () => {
          await axios.post(
            `${API}/serviceorder-numbers/${form.so}/cancel`,
            null,
            { headers: { Authorization: `Bearer ${token}` } }
          );
          registerBlocker(false, null)
          setShowLeaveModal(false);
          navigate(pendingNavigation);
        }}
      />

    <div className="min-h-screen bg-gray-100 p-8 pb-32">
      <h1 className="text-2xl font-bold mb-6">Serviceorder Sullair</h1>

      <div className="bg-white rounded-2xl shadow p-6 space-y-8">
        {/* SERVICEORDER BLOK */}
        <div>
          <h2 className="font-semibold mb-2">Serviceorder *</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label>Serviceorder nr *</label>
                <input
                  className="w-full border rounded px-3 py-2"
                  disabled={soReserved || soLocked}
                  value={form.so}
                  onChange={(e) => updateField("so", e.target.value)}
                />

                {!form.so && (
                  <button
                    type="button"
                    variant="primary"
                    onClick={reserveServiceOrderNumber}
                  >
                    ➕ Nieuw serviceordernummer
                  </button>
                )}
              

            </div>

            <div>
              <label>Klantreferentie</label>
              <input
                className="w-full border rounded px-3 py-2"
                value={form.customer_ref}
                onChange={(e) => updateField("customer_ref", e.target.value)}
              />
            </div>

            <div>
              <label>Inkoopnummer (PO)</label>
              <input
                className="w-full border rounded px-3 py-2"
                value={form.po}
                onChange={(e) => updateField("po", e.target.value)}
              />
            </div>



            <div>
              <label>Status</label>

              <select
                className="w-full border rounded px-3 py-2"
                value=""
                onChange={(e) => changeStatus(e.target.value)}
                disabled={!allowedStatuses.length}
              >
                {/* Huidige status (read-only) */}
                <option value="" disabled>
                  {form.status || "-- status --"}
                </option>

                {/* Toegestane volgende statussen */}
                {allowedStatuses.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
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
                onChange={(e) =>
                  setSelectedCustomerId(e.target.value ? Number(e.target.value) : null)
                }
              >
                <option value="">-- kies klant --</option>
                {customers.map((c) => (
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
                onChange={(e) =>
                  setSelectedContactId(e.target.value ? Number(e.target.value) : null)
                }
                disabled={!contacts.length}
              >
                <option value="">-- kies contactpersoon --</option>
                {contacts.map((ct) => (
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
                value={form.price_type || ""}
              />
            </div>

            <div>
              <label>Leverancier</label>
              <select
                className="w-full border rounded px-3 py-2"
                value={selectedSupplierId || ""}
                onChange={(e) => setSelectedSupplierId(Number(e.target.value))}
              >
                <option value="">-- kies leverancier --</option>
                {suppliers.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="success" onClick={saveOrder} disabled={loadingOrder}>
            {loadingOrder ? "Laden..." : "Serviceorder opslaan"}
          </Button>

          {soFromUrl && (
            <span className="text-sm text-gray-500">
              (geopend vanuit overzicht: {soFromUrl})
            </span>
          )}
        </div>

        {/* ARTIKELEN */}
        {soLocked && (
          <div>
            <h2 className="font-semibold mt-6">Artikelen</h2>

            <div className="flex gap-2 mt-2">
              <input
                className="border rounded px-3 py-2"
                placeholder="Part nr"
                value={newPartNo}
                onChange={(e) => setNewPartNo(e.target.value)}
              />

              <Button variant="primary" onClick={addArticle}>
                Toevoegen
              </Button>
            </div>

            {loadingItems ? (
              <div className="mt-3 text-gray-600">Artikelen laden...</div>
            ) : (
              <table className="w-full mt-3 border text-sm">
                <thead>
                  <tr className="bg-gray-200">
                    <th className="border p-2">Part nr</th>
                    <th className="border p-2">Omschrijving</th>
                    <th className="border p-2 text-center">Aantal</th>
                    <th className="border p-2 text-center">Leadtime</th>
                    <th className="border p-2 text-right">Bruto</th>
                    <th className="border p-2 text-right">WVK</th>
                    <th className="border p-2 text-right">Edmac</th>
                    <th className="border p-2 text-center">Bestel</th>
                    <th className="border p-2 text-center">Ontvangen</th>
                    <th className="border p-2 text-center"></th>
                  </tr>
                </thead>

                <tbody>
                  {items.map((it, i) => {
                    const isOrdered = it.bestellen === true;
                    const isReceived = it.ontvangen === true;

                    return (
                      <tr
                        key={i}
                        className={
                          isReceived ? "bg-blue-200" : isOrdered ? "bg-green-100" : ""
                        }
                      >
                        <td className="border p-1">{it.part_no}</td>
                        <td className="border p-1">{it.description}</td>

                        <td className="border p-1 text-center">
                          <input
                            className="w-20 border rounded px-2 py-1 text-center"
                            type="number"
                            disabled={isReceived}
                            value={formatQty(it.qty)}
                            onChange={(e) => {
                              const qty = Number(e.target.value);
                              setItems((prev) => {
                                const cp = [...prev];
                                cp[i] = { ...cp[i], qty };
                                return cp;
                              });
                            }}
                          />
                        </td>

                        <td className="border p-1 text-center">
                          <input
                            className="w-28 border rounded px-2 py-1 text-center"
                            placeholder="e.g. 2 weeks"
                            value={it.leadtime || ""}
                            onChange={(e) => {
                              const val = e.target.value;
                              setItems((prev) => {
                                const cp = [...prev];
                                cp[i] = { ...cp[i], leadtime: val };
                                return cp;
                              });
                            }}
                          />
                        </td>

                        <td className="border p-1 text-right">
                          {formatCurrency(it.price_bruto)}
                        </td>
                        <td className="border p-1 text-right">
                          {formatCurrency(it.price_wvk)}
                        </td>
                        <td className="border p-1 text-right">
                          {formatCurrency(it.price_edmac)}
                        </td>

                        {/* Bestellen */}
                        <td className="border p-1 text-center">
                          {!isReceived && (
                            <input
                              type="checkbox"
                              className="w-5 h-5"
                              checked={it.bestellen || false}
                              onChange={(e) => {
                                const checked = e.target.checked;
                                setItems((prev) => {
                                  const cp = [...prev];
                                  cp[i] = { ...cp[i], bestellen: checked };
                                  return cp;
                                });
                              }}
                            />
                          )}
                        </td>

                        {/* Ontvangen */}
                        <td className="border p-1 text-center">
                          {isOrdered && (
                            <input
                              type="checkbox"
                              className="w-5 h-5"
                              checked={it.ontvangen || false}
                              disabled={it.ontvangen}
                              onChange={() => markItemReceived(it)}
                            />
                          )}
                        </td>

                        {/* Verwijderen */}
                        <td className="border p-1 text-center">
                          {!isOrdered && (
                            <button
                              className="text-red-600 hover:text-red-800"
                              onClick={() => {
                                setItems((prev) => prev.filter((_, idx) => idx !== i));
                              }}
                            >
                              ✖
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}

        <h3 className="font-semibold mt-6">Historie</h3>

        <div className="border rounded bg-gray-50 text-sm max-h-60 overflow-auto">
          {log.length === 0 && (
            <div className="px-3 py-2 text-gray-500 italic">Nog geen gebeurtenissen</div>
          )}

          {log.map((l) => (
            <div key={l.id} className="border-b px-3 py-2">
              <b>{l.action}</b> – {l.message}
              <div className="text-xs text-gray-500">
                {new Date(l.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>

        {/* ===== MAIL MODAL ===== */}
        {showMailModal && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
            <div className="bg-white w-3/4 max-w-4xl p-6 rounded shadow">
              <h2 className="text-xl font-bold mb-4">Mail concept</h2>

              <div className="mb-2">
                <b>Aan:</b> {mailPreview.to}
              </div>

              <div className="mb-2">
                <b>Onderwerp:</b>
                <input
                  className="w-full border p-2"
                  value={mailPreview.subject}
                  onChange={(e) =>
                    setMailPreview({ ...mailPreview, subject: e.target.value })
                  }
                />
              </div>

              {/* 📎 PDF bijlage */}
              {mailPreview.pdf && (
                <div className="mb-3 p-2 border rounded bg-gray-100 text-sm">
                  📎 Bijlage: <b>{mailPreview.pdf}</b>
                </div>
              )}

              {/* Body */}
              <div className="mt-2">
                {editMode ? (
                  <textarea
                    className="w-full h-64 border p-2 font-mono text-sm"
                    value={mailPreview.body_html}
                    onChange={(e) =>
                      setMailPreview({
                        ...mailPreview,
                        body_html: e.target.value,
                      })
                    }
                  />
                ) : (
                  <div className="border rounded p-3 bg-white max-h-64 overflow-auto">
                    <div dangerouslySetInnerHTML={{ __html: mailPreview.body_html }} />
                  </div>
                )}
              </div>

              {/* Actie knoppen */}
              <div className="flex justify-between items-center mt-4">
                {/* Links: PDF bekijken */}
                <div>
                  {mailPreview.pdf && (
                    <button
                      onClick={openPdfPreview}
                      className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800"
                    >
                      📄 PDF bekijken
                    </button>
                  )}
                </div>

                {/* Rechts: acties */}
                <div className="flex gap-3">
                  <Button variant="secondary" onClick={() => setShowMailModal(false)}>
                    Annuleren
                  </Button>

                  <Button variant="primary" onClick={sendMail}>
                    Verzenden
                  </Button>

                  <button
                    className="text-sm text-blue-700 underline"
                    onClick={() => setEditMode(!editMode)}
                  >
                    {editMode ? "Voorbeeld tonen" : "Tekst bewerken"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showPackingSlipModal && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
            <div className="bg-white w-full max-w-md p-6 rounded shadow">
              <h2 className="text-xl font-bold mb-4">Pakbon genereren</h2>

              {/* Keuzes */}
              <div className="space-y-3">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={packingSlipOptions.customer}
                    onChange={(e) =>
                      setPackingSlipOptions((p) => ({
                        ...p,
                        customer: e.target.checked,
                      }))
                    }
                  />
                  Pakbon voor klant
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={packingSlipOptions.internal}
                    onChange={(e) =>
                      setPackingSlipOptions((p) => ({
                        ...p,
                        internal: e.target.checked,
                      }))
                    }
                  />
                  Pakbon intern
                </label>
              </div>

              {/* Acties */}
              <div className="flex justify-end gap-3 mt-6">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setShowPackingSlipModal(false);
                    setPackingSlipOptions({ customer: false, internal: false });
                  }}
                >
                  Sluiten
                </Button>

                <Button
                  variant="primary"
                  disabled={!hasPackingSlipSelection}
                  onClick={previewPackingSlip}
                >
                  Preview
                </Button>


                <Button
                  variant="succes"
                  disabled={!hasPackingSlipSelection}
                  onClick={printPackingSlip}
                >
                  Afdrukken
                </Button>
              </div>
            </div>
          </div>
        )}

        {showUnknownArticleModal && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
            <div className="bg-white w-full max-w-md p-6 rounded shadow">
              <h2 className="text-xl font-bold mb-4">Artikel onbekend</h2>

              <p className="mb-4">
                Artikelnummer <b>{unknownPartNo}</b> staat niet in de duallist.
                <br />
                Toch toevoegen als <i>NOT IN DUALLIST</i>?
              </p>

              <div className="flex justify-end gap-3">
                <button
                  className="px-4 py-2 bg-gray-400 text-white rounded"
                  onClick={() => {
                    setShowUnknownArticleModal(false);
                    setUnknownPartNo("");
                  }}
                >
                  Nee
                </button>

                <button
                  className="px-4 py-2 bg-green-600 text-white rounded"
                  onClick={addUnknownArticle}
                >
                  Ja, toevoegen
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {soLocked && (
        <ActionBar>
          {/* Links: “veilige” acties */}
          <div className="flex flex-wrap gap-3">
            <Button variant="success" onClick={saveItems}>
              Artikelen opslaan
            </Button>

            <Button variant="primary" onClick={openSullairMailPreview}>
              Aanvraag bij Sullair
            </Button>

            <Button variant="secondary" onClick={openOfferPreview}>
              Offerte versturen
            </Button>

            <div className="relative group">
              <Button
                variant="secondary"
                disabled={!hasOrderedItems}
                onClick={openOrderConfirmationPreview}
              >
                Bestelbevestiging klant
              </Button>

              {!hasOrderedItems && (
                <div
                  className="
                    absolute bottom-full mb-2 left-1/2 -translate-x-1/2
                    whitespace-nowrap
                    bg-gray-800 text-white text-xs
                    px-3 py-1 rounded
                    opacity-0 group-hover:opacity-100
                    transition
                    pointer-events-none
                    z-50
                  "
                >
                  Selecteer minimaal één artikel om te bestellen
                </div>
              )}
            </div>
          </div>

          {/* Rechts: proces / “impactvolle” acties */}
          <div className="flex flex-wrap gap-3">
            <div className="relative group">
              <Button
                variant="danger"
                disabled={!hasOrderedItems}
                onClick={openStockOrderPreview}
              >
                Bestellen
              </Button>

              {!hasOrderedItems && (
                <div
                  className="
                    absolute bottom-full mb-2 left-1/2 -translate-x-1/2
                    whitespace-nowrap
                    bg-gray-800 text-white text-xs
                    px-3 py-1 rounded
                    opacity-0 group-hover:opacity-100
                    transition
                    pointer-events-none
                    z-50
                  "
                >
                  Selecteer minimaal één artikel om te bestellen
                </div>
              )}
            </div>

            {hasReceivedItems && (
              <Button
                variant="secondary"
                onClick={() => setShowPackingSlipModal(true)}
              >
                📦 Pakbon genereren
              </Button>
            )}
          </div>
        </ActionBar>
      )}

              

    </div>
  </>  
  );
}
