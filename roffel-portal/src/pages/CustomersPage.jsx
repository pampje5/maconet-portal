import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export default function CustomersPage() {
  const API = "http://127.0.0.1:8000";
  const token = localStorage.getItem("token");

  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const [contacts, setContacts] = useState([]);
  const [editingContactId, setEditingContactId] = useState(null);
  const [editContact, setEditContact] = useState({
    contact_name: "",
    email: "",
  });



  // ---- Nieuw klant formulier ----
  const [newCustomer, setNewCustomer] = useState({
    name: "",
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
    const res = await axios.get(`${API}/customers`, {
      headers: {
        "x-api-key": "CHANGE_ME",
        Authorization: `Bearer ${token}`,
      },
    });

    setCustomers(res.data);
  }

  async function loadContacts(customerId) {
    const res = await axios.get(`${API}/customers/${customerId}/contacts`, {
      headers: {
        "x-api-key": "CHANGE_ME",
        Authorization: `Bearer ${token}`,
      },
    });

    setContacts(res.data);
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  // ======================
  // SELECT CUSTOMER
  // ======================
  function handleSelect(id) {
    const cust = customers.find((c) => c.id === Number(id));
    setSelectedCustomer(cust);
    loadContacts(id);
  }

  // ======================
  // CREATE CUSTOMER
  // ======================
  async function createCustomer() {
    try {
      await axios.post(`${API}/customers`, newCustomer, {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`,
        },
      });

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

    await axios.delete(`${API}/customers/${selectedCustomer.id}`, {
      headers: {
        "x-api-key": "CHANGE_ME",
        Authorization: `Bearer ${token}`,
      },
    });

    toast.success("Klant verwijderd");

    setSelectedCustomer(null);
    setContacts([]);
    loadCustomers();
  }

  // ======================
  // SAVE SETTINGS
  // ======================
  async function saveCustomerSettings() {
    await axios.put(
      `${API}/customers/${selectedCustomer.id}`,
      selectedCustomer,
      {
        headers: {
          "x-api-key": "CHANGE_ME",
          Authorization: `Bearer ${token}`,
        },
      }
    );

    toast.success("Klant opgeslagen");
    loadCustomers();
  }

  // ======================
  // ADD CONTACT
  // ======================
  async function addContact() {
    await axios.post(
      `${API}/customers/${selectedCustomer.id}/contacts`,
      newContact
    );

    setNewContact({ contact_name: "", email: "" });
    loadContacts(selectedCustomer.id);
  }

  // ======================
  // DELETE CONTACT
  // ======================
  async function removeContact(id) {
    await axios.delete(`${API}/contacts/${id}`);
    loadContacts(selectedCustomer.id);
  }

  // ======================
  // EDIT CONTACT
  // ======================
  async function saveEditedContact(id) {
    await axios.put(`${API}/contacts/${id}`, editContact);
    setEditingContactId(null);
    loadContacts(selectedCustomer.id);
  }

  // ======================
  // SET CONTACT Primary
  // ======================
  async function setPrimaryContact(id) {
    try {
      await axios.post(`${API}/contacts/${id}/set_primary`);
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

      <h1 className="text-2xl font-bold mb-6">
        Klantenbeheer
      </h1>

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

        {/* ------------------- MIDDEN: SELECTEER KLANT ------------------- */}
        <div className="bg-white p-6 rounded-2xl shadow">

          <h2 className="font-semibold mb-3">Selecteer klant</h2>

          <select
            className="w-full border rounded px-3 py-2"
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
            <button
              className="mt-4 bg-red-600 text-white rounded px-4 py-2"
              onClick={deleteCustomer}
            >
              Klant verwijderen
            </button>
          )}
        </div>

        {/* ------------------- RECHTS: INSTELLINGEN & CONTACTEN ------------------- */}
        {selectedCustomer && (
          <div className="bg-white p-6 rounded-2xl shadow space-y-6">

            {/* klantinstellingen */}
            <div>
              <h2 className="font-semibold mb-2">Klantinstellingen</h2>

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
                <option value="">-- prijs type --</option>
                <option value="LIST">LIST</option>
                <option value="BRUTO">BRUTO</option>
                <option value="WVK">WVK</option>
                <option value="EDMAC">EDMAC</option>
              </select>

              <button
                onClick={saveCustomerSettings}
                className="mt-3 bg-blue-600 text-white rounded px-4 py-2"
              >
                Opslaan
              </button>
            </div>

            <hr />

            {/* contactpersonen */}
            <div>
              <h2 className="font-semibold mb-2">Contactpersonen</h2>

              {contacts.map((ct) => (
                <div key={ct.id} className="border rounded p-2 mb-1">

                  {editingContactId === ct.id ? (
                    <>
                      <input
                        className="w-full border rounded px-2 py-1 mb-1"
                        value={editContact.contact_name}
                        onChange={(e) =>
                          setEditContact({ ...editContact, contact_name: e.target.value })
                        }
                      />

                      <input
                        className="w-full border rounded px-2 py-1 mb-1"
                        value={editContact.email}
                        onChange={(e) =>
                          setEditContact({ ...editContact, email: e.target.value })
                        }
                      />

                      <button
                        className="bg-green-600 text-white px-3 py-1 rounded mr-2"
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
                    </>
                  ) : (
                    <div className="flex justify-between">

                      <span>
                        {ct.contact_name} — {ct.email}
                        {ct.is_primary ? " ⭐" : ""}
                      </span>

                      <div className="space-x-3 flex items-center">

                        {!ct.is_primary && (
                          <button
                            className="text-yellow-600"
                            onClick={() => setPrimaryContact(ct.id)}
                          >
                            ⭐ maak primair
                          </button>
                        )}
                        
                        <button
                          className="text-blue-700"
                          onClick={() => {
                            setEditingContactId(ct.id);
                            setEditContact(ct);
                          }}
                        >
                          ✎
                        </button>

                        <button
                          className="text-red-600"
                          onClick={() => removeContact(ct.id)}
                        >
                         ✖
                        </button>
                      </div>
                    </div>
                  )}

                </div>
              ))}


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
                className="mt-2 bg-green-600 text-white rounded px-4 py-2"
              >
                Contact toevoegen
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
