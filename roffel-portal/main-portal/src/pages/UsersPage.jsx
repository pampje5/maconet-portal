import { useEffect, useState } from "react";
import api from "../api";
import toast from "react-hot-toast";
import CreateUserModal from "../components/CreateUserModal";


export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [me, setMe] = useState(null)


  async function loadUsers() {
    try {
      const res = await api.get("/users");
      setUsers(res.data);
    } catch (err) {
      toast.error("Gebruikers laden mislukt");
    } finally {
      setLoading(false);
    }
  }

  async function loadMe() {
  try {
    const res = await api.get("/auth/whoami");
    setMe(res.data);
  } catch {
    setMe(null);
  }
}



  useEffect(() => {
    loadUsers();
    loadMe();
  }, []);

  if (loading) {
    return <div className="p-8">Laden…</div>;
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Gebruikers</h1>

      {me?.role !== "user" && (
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          onClick={() => setShowCreate(true)}
        >
          + Nieuwe gebruiker
        </button>
      )}
      </div>

      <div className="bg-white rounded-xl shadow">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Naam</th>
              <th className="p-3 text-left">Email</th>
              <th className="p-3 text-left">Functie</th>
              <th className="p-3 text-left">Rol</th>
              <th className="p-3 text-left">Acties</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t">
              <td className="p-3">
                {[u.first_name, u.last_name].filter(Boolean).join(" ") || "—"}
              </td>

              <td className="p-3">{u.email}</td>

              <td className="p-3">
                {u.function || "—"}
              </td>

                <td className="p-3">
                  <select
                    value={u.role}
                    disabled={
                      !me ||
                      me.id === u.id ||              // jezelf niet
                      (me.role === "admin" && u.role === "developer")
                    }
                    onChange={async (e) => {
                      try {
                        
                        await api.post(
                          `/users/${u.id}/set-role`,
                          { role: e.target.value });
                        toast.success("Rol aangepast");
                        loadUsers();
                      } catch {
                        toast.error("Rol wijzigen mislukt");
                      }
                    }}
                    className="border rounded px-2 py-1"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                    {me?.role === "developer" && (
                      <option value="developer">Developer</option>
                    )}
                  </select>
                </td>

                <td className="p-3">
                  {me &&
                    me.id !== u.id &&
                    me.role === "developer" &&
                    (
                      <button
                        onClick={async () => {
                          if (!window.confirm(`Gebruiker ${u.email} verwijderen?`)) return;

                          try {
                            
                            await api.delete(`/users/${u.id}`);
                            toast.success("Gebruiker verwijderd");
                            loadUsers();
                          } catch {
                            toast.error("Verwijderen mislukt");
                          }
                        }}
                        className="text-red-600 hover:underline"
                      >
                        Verwijderen
                      </button>
                    )
                  }
                </td>

              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showCreate && (
        <CreateUserModal
          onClose={() => setShowCreate(false)}
          onCreated={loadUsers}
        />
      )}


    </div>
  );
}
