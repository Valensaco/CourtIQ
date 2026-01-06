import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Admin.css';

const API_BASE = 'http://127.0.0.1:5000';

function Admin() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [members, setMembers] = useState([]);
  const [coaches, setCoaches] = useState([]);
  const [courts, setCourts] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({});
  const [revenueData, setRevenueData] = useState([]);
  const [chartPeriod, setChartPeriod] = useState(30);

useEffect(() => {
  if (activeTab === 'dashboard') {
    loadStats();
    loadRevenueChart();
  }
  if (activeTab === 'members') loadMembers();
  if (activeTab === 'coaches') loadCoaches();
  if (activeTab === 'courts') loadCourts();
  if (activeTab === 'bookings') loadBookings();
}, [activeTab, chartPeriod]);

  const loadStats = async () => {
    const res = await axios.get(`${API_BASE}/admin/stats`);
    setStats(res.data);
  };

  const loadRevenueChart = async (days = chartPeriod) => {
  const res = await axios.get(`${API_BASE}/admin/revenue-chart?days=${days}`);
  setRevenueData(res.data);
};

  const loadMembers = async () => {
    const res = await axios.get(`${API_BASE}/admin/members`);
    setMembers(res.data);
  };

  const loadCoaches = async () => {
    const res = await axios.get(`${API_BASE}/admin/coaches`);
    setCoaches(res.data);
  };

  const loadCourts = async () => {
    const res = await axios.get(`${API_BASE}/admin/courts`);
    setCourts(res.data);
  };

  const loadBookings = async () => {
    const res = await axios.get(`${API_BASE}/admin/bookings`);
    setBookings(res.data);
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/admin/members`, formData);
    setShowAddForm(false);
    setFormData({});
    loadMembers();
  };

  const handleAddCoach = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/admin/coaches`, formData);
    setShowAddForm(false);
    setFormData({});
    loadCoaches();
  };

  const handleAddCourt = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/admin/courts`, formData);
    setShowAddForm(false);
    setFormData({});
    loadCourts();
  };

  const handleAddBooking = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/admin/bookings`, formData);
    setShowAddForm(false);
    setFormData({});
    loadBookings();
  };

  const handleDelete = async (type, id) => {
    if (!window.confirm('Are you sure?')) return;
    await axios.delete(`${API_BASE}/admin/${type}/${id}`);
    if (type === 'members') loadMembers();
    if (type === 'coaches') loadCoaches();
    if (type === 'courts') loadCourts();
    if (type === 'bookings') loadBookings();
  };

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>🎾 CourtIQ Admin</h1>
        <nav className="admin-nav">
          <button onClick={() => { setActiveTab('dashboard'); setShowAddForm(false); }}
                  className={activeTab === 'dashboard' ? 'active' : ''}>
            Dashboard
          </button>
          <button onClick={() => { setActiveTab('members'); setShowAddForm(false); }}
                  className={activeTab === 'members' ? 'active' : ''}>
            Members
          </button>
          <button onClick={() => { setActiveTab('coaches'); setShowAddForm(false); }}
                  className={activeTab === 'coaches' ? 'active' : ''}>
            Coaches
          </button>
          <button onClick={() => { setActiveTab('courts'); setShowAddForm(false); }}
                  className={activeTab === 'courts' ? 'active' : ''}>
            Courts
          </button>
          <button onClick={() => { setActiveTab('bookings'); setShowAddForm(false); }}
                  className={activeTab === 'bookings' ? 'active' : ''}>
            Bookings
          </button>
          <a href="/" className="chat-link">Go to Chat →</a>
        </nav>
      </header>

      <div className="admin-content">
        {activeTab === 'dashboard' && stats && (
  <div className="dashboard">
    <div className="stat-card">
      <h3>Total Members</h3>
      <p className="stat-value">{stats.total_members}</p>
    </div>
    <div className="stat-card">
      <h3>Total Revenue</h3>
      <p className="stat-value">${stats.total_revenue}</p>
    </div>
    <div className="stat-card">
      <h3>Bookings This Month</h3>
      <p className="stat-value">{stats.bookings_this_month}</p>
    </div>
    <div className="stat-card">
      <h3>Revenue This Month</h3>
      <p className="stat-value">${stats.revenue_this_month}</p>
    </div>
  </div>
)}

{activeTab === 'dashboard' && revenueData.length > 0 && (
  <div className="chart-container">
    <div className="chart-header">
      <h3>Revenue Overview</h3>
      <div className="chart-period-selector">
        <button
          className={chartPeriod === 30 ? 'active' : ''}
          onClick={() => setChartPeriod(30)}>
          30 Days
        </button>
        <button
          className={chartPeriod === 90 ? 'active' : ''}
          onClick={() => setChartPeriod(90)}>
          3 Months
        </button>
        <button
          className={chartPeriod === 180 ? 'active' : ''}
          onClick={() => setChartPeriod(180)}>
          6 Months
        </button>
        <button
          className={chartPeriod === 365 ? 'active' : ''}
          onClick={() => setChartPeriod(365)}>
          1 Year
        </button>
      </div>
    </div>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={revenueData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="revenue" stroke="#667eea" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  </div>
)}




        {activeTab === 'members' && (
          <div>
            <div className="section-header">
              <h2>Members</h2>
              <button onClick={() => { setShowAddForm(true); setFormData({}); }} className="add-btn">
                + Add Member
              </button>
            </div>

            {showAddForm && (
              <form onSubmit={handleAddMember} className="add-form">
                <input placeholder="Name" required
                       onChange={e => setFormData({...formData, name: e.target.value})} />
                <input placeholder="Email" type="email" required
                       onChange={e => setFormData({...formData, email: e.target.value})} />
                <input placeholder="Phone"
                       onChange={e => setFormData({...formData, phone: e.target.value})} />
                <select required onChange={e => setFormData({...formData, membership_tier: e.target.value})}>
                  <option value="">Select Tier</option>
                  <option value="Premium">Premium</option>
                  <option value="Standard">Standard</option>
                  <option value="Junior">Junior</option>
                </select>
                <input type="date" required
                       onChange={e => setFormData({...formData, join_date: e.target.value})} />
                <div className="form-actions">
                  <button type="submit">Save</button>
                  <button type="button" onClick={() => setShowAddForm(false)}>Cancel</button>
                </div>
              </form>
            )}

            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Tier</th>
                  <th>Join Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map(m => (
                  <tr key={m.member_id}>
                    <td>{m.name}</td>
                    <td>{m.email}</td>
                    <td>{m.membership_tier}</td>
                    <td>{m.join_date}</td>
                    <td>{m.status}</td>
                    <td>
                      <button onClick={() => handleDelete('members', m.member_id)} className="delete-btn">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'coaches' && (
          <div>
            <div className="section-header">
              <h2>Coaches</h2>
              <button onClick={() => { setShowAddForm(true); setFormData({}); }} className="add-btn">
                + Add Coach
              </button>
            </div>

            {showAddForm && (
              <form onSubmit={handleAddCoach} className="add-form">
                <input placeholder="Name" required
                       onChange={e => setFormData({...formData, name: e.target.value})} />
                <input placeholder="Specialty"
                       onChange={e => setFormData({...formData, specialty: e.target.value})} />
                <input placeholder="Hourly Rate" type="number" step="0.01" required
                       onChange={e => setFormData({...formData, hourly_rate: e.target.value})} />
                <input placeholder="Weekly Hours" type="number"
                       onChange={e => setFormData({...formData, weekly_available_hours: e.target.value})} />
                <div className="form-actions">
                  <button type="submit">Save</button>
                  <button type="button" onClick={() => setShowAddForm(false)}>Cancel</button>
                </div>
              </form>
            )}

            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Specialty</th>
                  <th>Hourly Rate</th>
                  <th>Weekly Hours</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {coaches.map(c => (
                  <tr key={c.coach_id}>
                    <td>{c.name}</td>
                    <td>{c.specialty}</td>
                    <td>${c.hourly_rate}</td>
                    <td>{c.weekly_available_hours}</td>
                    <td>
                      <button onClick={() => handleDelete('coaches', c.coach_id)} className="delete-btn">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'courts' && (
          <div>
            <div className="section-header">
              <h2>Courts</h2>
              <button onClick={() => { setShowAddForm(true); setFormData({}); }} className="add-btn">
                + Add Court
              </button>
            </div>

            {showAddForm && (
              <form onSubmit={handleAddCourt} className="add-form">
                <input placeholder="Court Name" required
                       onChange={e => setFormData({...formData, court_name: e.target.value})} />
                <select required onChange={e => setFormData({...formData, surface_type: e.target.value})}>
                  <option value="">Select Surface</option>
                  <option value="hard">Hard</option>
                  <option value="clay">Clay</option>
                  <option value="grass">Grass</option>
                </select>
                <label>
                  <input type="checkbox"
                         onChange={e => setFormData({...formData, indoor: e.target.checked ? 1 : 0})} />
                  Indoor
                </label>
                <div className="form-actions">
                  <button type="submit">Save</button>
                  <button type="button" onClick={() => setShowAddForm(false)}>Cancel</button>
                </div>
              </form>
            )}

            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Surface</th>
                  <th>Indoor</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {courts.map(c => (
                  <tr key={c.court_id}>
                    <td>{c.court_name}</td>
                    <td>{c.surface_type}</td>
                    <td>{c.indoor ? 'Yes' : 'No'}</td>
                    <td>
                      <button onClick={() => handleDelete('courts', c.court_id)} className="delete-btn">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'bookings' && (
          <div>
            <div className="section-header">
              <h2>Bookings</h2>
              <button onClick={() => {
                setShowAddForm(true);
                setFormData({});
                loadMembers();
                loadCoaches();
                loadCourts();
              }} className="add-btn">
                + Add Booking
              </button>
            </div>

            {showAddForm && (
              <form onSubmit={handleAddBooking} className="add-form booking-form">
                <select required onChange={e => setFormData({...formData, member_id: e.target.value})}>
                  <option value="">Select Member</option>
                  {members.map(m => <option key={m.member_id} value={m.member_id}>{m.name}</option>)}
                </select>
                <select onChange={e => setFormData({...formData, coach_id: e.target.value || null})}>
                  <option value="">Select Coach (Optional)</option>
                  {coaches.map(c => <option key={c.coach_id} value={c.coach_id}>{c.name}</option>)}
                </select>
                <select required onChange={e => setFormData({...formData, court_id: e.target.value})}>
                  <option value="">Select Court</option>
                  {courts.map(c => <option key={c.court_id} value={c.court_id}>{c.court_name}</option>)}
                </select>
                <select required onChange={e => setFormData({...formData, lesson_type: e.target.value})}>
                  <option value="">Lesson Type</option>
                  <option value="private">Private</option>
                  <option value="semi-private">Semi-Private</option>
                  <option value="group">Group</option>
                  <option value="court-rental">Court Rental</option>
                </select>
                <input type="date" required
                       onChange={e => setFormData({...formData, booking_date: e.target.value})} />
                <input type="time" required placeholder="Start Time"
                       onChange={e => setFormData({...formData, start_time: e.target.value})} />
                <input type="time" required placeholder="End Time"
                       onChange={e => setFormData({...formData, end_time: e.target.value})} />
                <input type="number" required placeholder="Duration (minutes)"
                       onChange={e => setFormData({...formData, duration_minutes: e.target.value})} />
                <input type="number" step="0.01" required placeholder="Price"
                       onChange={e => setFormData({...formData, price: e.target.value})} />
                <div className="form-actions">
                  <button type="submit">Save</button>
                  <button type="button" onClick={() => setShowAddForm(false)}>Cancel</button>
                </div>
              </form>
            )}

            <table className="bookings-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Member</th>
                  <th>Coach</th>
                  <th>Court</th>
                  <th>Type</th>
                  <th>Price</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map(b => (
                  <tr key={b.booking_id}>
                    <td>{b.booking_date}</td>
                    <td>{b.start_time}</td>
                    <td>{b.member_name}</td>
                    <td>{b.coach_name || 'N/A'}</td>
                    <td>{b.court_name}</td>
                    <td>{b.lesson_type}</td>
                    <td>${b.price}</td>
                    <td>{b.status}</td>
                    <td>
                      <button onClick={() => handleDelete('bookings', b.booking_id)} className="delete-btn">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Admin;