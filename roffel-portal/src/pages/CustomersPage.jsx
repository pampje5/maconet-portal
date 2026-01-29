
import { useState, useEffect } from "react";
import api from "../api"
import toast from "react-hot-toast";

export default function CustomersPage() {
 
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [priceRules, setPriceRules] = useState([]);
  const [loadingPriceRules, setLoadingPriceRules] = useState(false);

  const [contacts, setContacts] = useState([]);
  const [editingContactId, setEditingContactId] = useState(null);
  const [editContact, setEditContact] = useState({
    contact_name: "",
    email: "",
  });



  // ---- Nieuw klant formulier ----
  const [newCustomer, setNewCustomer] = useState({
    name: "",
    price_type: "",
  });

  // ---- Contact formulier ----
  const [newContact, setNewContact] = useState({
    contact_name: "",
    email: "",
  });

  // ======================
  // LOAD CUSTOMERS
  // ======================
  async function loadCustomers() {
    const res = await api.get("/customers");

    setCustomers(res.data);
  }

  async function loadContacts(customerId) {
    try {
      const res = await api.get(`/customers/${customerId}/contacts`);
      setContacts(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Kan contacten niet laden");
    }  
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadPriceRules(customerId) {setLoadingPriceRules(true);

    try {
      const res = await api.get(`/customers/${customerId}/price-rules`);
      setPriceRules(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Kon prijsstaffels niet laden");
    } finally {
      setLoadingPriceRules(false);
    }
  }

  // ======================
  // SELECT CUSTOMER
  // ======================
  async function handleSelect(id) {
  const cust = customers.find((c) => c.id === Number(id));
  setSelectedCustomer(cust);
  loadContacts(id);

  if (!id) {
    setPriceRules([]);
    setSelectedCustomer(null);
    setContacts([]);
    return;
  }

  try {
    setLoadingPriceRules(true);

    const res = await api.get(
      `/customers/${id}/price-rules`
      
    );

    setPriceRules(res.data);
  } catch (err) {
    console.error(err);
    toast.error("Kon prijsregels niet laden");
  } finally {
    setLoadingPriceRules(false);
  }
}



  // ======================
  // CREATE CUSTOMER
  // ======================
  async function createCustomer() {
    try {
      await api.post("/customers", newCustomer);

      toast.success("Klant aangemaakt");
      setNewCustomer({ name: "", price_type: "" });
      loadCustomers();
    } catch (e) {
      console.error(e);
      toast.error("Aanmaken mislukt");
    }
  }

  // ======================
  // DELETE CUSTOMER
  // ======================
  async function deleteCustomer() {
    if (!selectedCustomer) return;

    if (!window.confirm("Weet je zeker dat je deze klant wilt verwijderen?"))
      return;

    await api.delete(`/customers/${selectedCustomer.id}`);

    toast.success("Klant verwijderd");

    setSelectedCustomer(null);
    setContacts([]);
    loadCustomers();
  }

  // ======================
  // SAVE SETTINGS
  // ======================
  async function saveCustomerSettings() {
    await api.put(
      `/customers/${selectedCustomer.id}`,
      selectedCustomer);

    toast.success("Klant opgeslagen");
    loadCustomers();
  }

  // ======================
  // ADD CONTACT
  // ======================
  async function addContact() {
    await api.post(
      `/customers/${selectedCustomer.id}/contacts`,
      newContact);

    setNewContact({ contact_name: "", email: "" });
    loadContacts(selectedCustomer.id);
  }

  // ======================
  // DELETE CONTACT
  // ======================
  async function removeContact(contactId) {
    await api.delete(`/customers/${selectedCustomer.id}/contacts/${contactId}`);
    loadContacts(selectedCustomer.id);
  }

  // ======================
  // EDIT CONTACT
  // ======================
  async function saveEditedContact(contactId) {
    await api.put(
      `/customers/${selectedCustomer.id}/contacts/${contactId}`, 
      editContact,
    );

    setEditingContactId(null);
    loadContacts(selectedCustomer.id);
  }

  // ======================
  // SET CONTACT Primary
  // ======================
  async function setPrimaryContact(contactId) {
    try {
      await api.post(
        `/customers/${selectedCustomer.id}/contacts/${contactId}/set_primary`,
      null,
    );
      loadContacts(selectedCustomer.id);
    } catch (err) {
      console.error(err);
      alert("Instellen primaire contactpersoon mislukt");
    }
  }


  // ======================
  // UI
  // ======================

  return (
  <div className="min-h-screen p-8 bg-gray-100">
    <h1 className="text-2xl font-bold mb-6">Klantenbeheer</h1>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

      {/* ------------------- LINKS: NIEUWE KLANT ------------------- */}
      <div className="bg-white p-6 rounded-2xl shadow">
        <h2 className="font-semibold mb-3">Nieuwe klant</h2>

        <input
          className="w-full border rounded px-3 py-2 mb-3"
          placeholder="Klantnaam"
          value={newCustomer.name}
          onChange={(e) =>
            setNewCustomer({ ...newCustomer, name: e.target.value })
          }
        />

        <button
          onClick={createCustomer}
          className="w-full bg-green-600 text-white rounded py-2"
        >
          Klant toevoegen
        </button>
      </div>

      {/* ------------------- MIDDEN: SELECTEER KLANT + INSTELLINGEN ------------------- */}
      <div className="bg-white p-6 rounded-2xl shadow space-y-4">
        <h2 className="font-semibold">Selecteer klant</h2>

        <select
          className="w-full border rounded px-3 py-2"
          value={selectedCustomer?.id || ""}
          onChange={(e) => handleSelect(e.target.value)}
        >
          <option value="">-- kies klant --</option>
          {customers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        {selectedCustomer && (
          <>
            <button
              className="bg-red-600 text-white rounded px-4 py-2"
              onClick={deleteCustomer}
            >
              Klant verwijderen
            </button>

            <hr />

            {/* KLANTINSTELLINGEN */}
            <div>
              <h3 className="font-semibold mb-2">Klantinstellingen</h3>

              <input
                className="w-full border rounded px-3 py-2 mb-2"
                value={selectedCustomer.name}
                onChange={(e) =>
                  setSelectedCustomer({
                    ...selectedCustomer,
                    name: e.target.value,
                  })
                }
              />

              <select
                className="w-full border rounded px-3 py-2"
                value={selectedCustomer.price_type || ""}
                onChange={(e) =>
                  setSelectedCustomer({
                    ...selectedCustomer,
                    price_type: e.target.value,
                  })
                }
              >
                <option value="">-- basis prijstype --</option>
                <option value="BRUTO">BRUTO</option>
                <option value="WVK">WVK</option>
                <option value="EDMAC">EDMAC</option>
              </select>
              
                <hr className="my-4" />

               <h3 className="font-semibold mb-2">Prijsstaffels</h3>

              {loadingPriceRules && <p>Laden...</p>}

              {!loadingPriceRules && (
                <div className="space-y-2">
                  {priceRules.map((rule, idx) => (
                    <div key={rule.id} className="flex gap-2 items-center">
                      <input
                        type="number"
                        className="w-32 border rounded px-2 py-1"
                        value={rule.min_amount}
                        onChange={(e) => {
                          const val = Number(e.target.value);
                          setPriceRules(prev => {
                            const copy = [...prev];
                            copy[idx] = { ...copy[idx], min_amount: val };
                            return copy;
                          });
                        }}
                      />

                      <select
                        className="border rounded px-2 py-1"
                        value={rule.price_type}
                        onChange={(e) => {
                          const val = e.target.value;
                          setPriceRules(prev => {
                            const copy = [...prev];
                            copy[idx] = { ...copy[idx], price_type: val };
                            return copy;
                          });
                        }}
                      >
                        <option value="LIST">LIST</option>
                        <option value="BRUTO">BRUTO</option>
                        <option value="WVK">WVK</option>
                        <option value="EDMAC">EDMAC</option>
                      </select>

                      <button
                        className="text-red-600"
                        onClick={() => {
                          setPriceRules(prev => prev.filter(r => r !== rule));
                        }}
                      >
                        ✖
                      </button>
                    </div>
                  ))}

                  <button
                    className="mt-2 text-blue-700"
                    onClick={() =>
                      setPriceRules(prev => [
                        ...prev,
                        { min_amount: 0, price_type: "BRUTO" },
                      ])
                    }
                  >
                    + Staffel toevoegen
                  </button>
                </div>
              )}

              <hr className="my-4" />

              {/* ===================== */}
              {/* 🏠 NAW GEGEVENS */}
              {/* ===================== */}
              <h3 className="font-semibold mb-2">Adresgegevens</h3>

              <input
                className="w-full border rounded px-3 py-2 mb-2"
                placeholder="Adres"
                value={selectedCustomer.address || ""}
                onChange={(e) =>
                  setSelectedCustomer({
                    ...selectedCustomer,
                    address: e.target.value,
                  })
                }
              />

              <div className="flex gap-2">
                <input
                  className="w-1/3 border rounded px-3 py-2"
                  placeholder="Postcode"
                  value={selectedCustomer.zipcode || ""}
                  onChange={(e) =>
                    setSelectedCustomer({
                      ...selectedCustomer,
                      zipcode: e.target.value,
                    })
                  }
                />

                <input
                  className="w-2/3 border rounded px-3 py-2"
                  placeholder="Plaats"
                  value={selectedCustomer.city || ""}
                  onChange={(e) =>
                    setSelectedCustomer({
                      ...selectedCustomer,
                      city: e.target.value,
                    })
                  }
                />
              </div>

              <input
                className="w-full border rounded px-3 py-2 mt-2"
                placeholder="Land"
                value={selectedCustomer.country || ""}
                onChange={(e) =>
                  setSelectedCustomer({
                    ...selectedCustomer,
                    country: e.target.value,
                  })
                }
              />

              <button
                onClick={async () => {
                  await saveCustomerSettings();

                  try {
                    await api.post(
                      `$/customers/${selectedCustomer.id}/price-rules`,
                      priceRules,
                      
                    );

                    toast.success("Klant + adres + prijsregels opgeslagen");
                  } catch (err) {
                    console.error(err);
                    toast.error("Opslaan mislukt");
                  }
                }}
                className="mt-4 bg-blue-600 text-white rounded px-4 py-2"
              >
                Opslaan
              </button>


            </div>
          </>
        )}
      </div>

      {/* ------------------- RECHTS: CONTACTPERSONEN ------------------- */}
      {selectedCustomer ? (
        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="font-semibold mb-3">Contactpersonen</h2>

          {contacts.map((ct) => (
            <div key={ct.id} className="border rounded p-2 mb-2">
              {editingContactId === ct.id ? (
                <>
                  <input
                    className="w-full border rounded px-2 py-1 mb-2"
                    value={editContact.contact_name}
                    onChange={(e) =>
                      setEditContact({
                        ...editContact,
                        contact_name: e.target.value,
                      })
                    }
                  />

                  <input
                    className="w-full border rounded px-2 py-1 mb-2"
                    value={editContact.email}
                    onChange={(e) =>
                      setEditContact({ ...editContact, email: e.target.value })
                    }
                  />

                  <div className="flex gap-2">
                    <button
                      className="bg-green-600 text-white px-3 py-1 rounded"
                      onClick={() => saveEditedContact(ct.id)}
                    >
                      Opslaan
                    </button>

                    <button
                      className="bg-gray-400 text-white px-3 py-1 rounded"
                      onClick={() => setEditingContactId(null)}
                    >
                      Annuleer
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex justify-between items-center gap-3">
                  <div className="min-w-0">
                    <div className="font-medium truncate">
                      {ct.contact_name} {ct.is_primary ? "⭐" : ""}
                    </div>
                    <div className="text-sm text-gray-600 truncate">{ct.email}</div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    {!ct.is_primary && (
                      <button
                        className="text-yellow-700"
                        onClick={() => setPrimaryContact(ct.id)}
                        title="Maak primair"
                      >
                        ⭐
                      </button>
                    )}

                    <button
                      className="text-blue-700"
                      onClick={() => {
                        setEditingContactId(ct.id);
                        setEditContact(ct);
                      }}
                      title="Bewerken"
                    >
                      ✎
                    </button>

                    <button
                      className="text-red-600"
                      onClick={() => removeContact(ct.id)}
                      title="Verwijderen"
                    >
                      ✖
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* nieuw contact */}
          <input
            className="w-full border rounded px-3 py-2 mt-2"
            placeholder="Naam"
            value={newContact.contact_name}
            onChange={(e) =>
              setNewContact({ ...newContact, contact_name: e.target.value })
            }
          />

          <input
            className="w-full border rounded px-3 py-2 mt-2"
            placeholder="Email"
            value={newContact.email}
            onChange={(e) =>
              setNewContact({ ...newContact, email: e.target.value })
            }
          />

          <button
            onClick={addContact}
            className="mt-3 bg-green-600 text-white rounded px-4 py-2"
          >
            Contact toevoegen
          </button>
        </div>
      ) : (
        // lege placeholder zodat grid netjes 3 kolommen blijft houden
        <div />
      )}
    </div>
  </div>
);
}