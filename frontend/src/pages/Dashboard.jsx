import { useState, useEffect, useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell,
  AreaChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis
} from 'recharts'
import API from '../api/auth'
import { KpiCard, Loading, EmptyState, fmt } from '../components/KpiCard'
import { FiDollarSign, FiTrendingUp, FiPercent, FiShoppingCart,
         FiTag, FiAlertTriangle, FiDownload, FiRefreshCw } from 'react-icons/fi'
import toast from 'react-hot-toast'

const COLORS = ['#2563eb', '#7c3aed', '#16a34a', '#d97706', '#dc2626', '#0891b2']

export default function Dashboard() {
  const location = useLocation()
  const navigate = useNavigate()

  const [datasets, setDatasets] = useState([])
  const [datasetId, setDatasetId] = useState(location.state?.datasetId || null)
  const [filters, setFilters] = useState({ region: '', category: '', date_from: '', date_to: '' })
  const [filterOptions, setFilterOptions] = useState({ regions: [], categories: [] })
  const [activeTab, setActiveTab] = useState('overview')

  const [kpis, setKpis] = useState(null)
  const [trend, setTrend] = useState([])
  const [regions, setRegions] = useState([])
  const [categories, setCategories] = useState([])
  const [topProducts, setTopProducts] = useState([])
  const [insights, setInsights] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [forecast, setForecast] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    API.get('/upload/datasets').then(({ data }) => {
      const ready = data.filter(d => d.status === 'ready')
      setDatasets(ready)
      if (!datasetId && ready.length > 0) setDatasetId(ready[0].id)
    }).catch(() => {})
  }, [])

  const buildParams = () => {
    const p = {}
    if (filters.region) p.region = filters.region
    if (filters.category) p.category = filters.category
    if (filters.date_from) p.date_from = filters.date_from
    if (filters.date_to) p.date_to = filters.date_to
    return p
  }

  const loadData = useCallback(async () => {
    if (!datasetId) return
    setLoading(true)
    const params = buildParams()
    try {
      const [kpiRes, trendRes, regRes, catRes, prodRes, insRes, filterRes] = await Promise.all([
        API.get(`/analytics/${datasetId}/kpis`, { params }),
        API.get(`/analytics/${datasetId}/trend`, { params }),
        API.get(`/analytics/${datasetId}/regions`, { params }),
        API.get(`/analytics/${datasetId}/categories`, { params }),
        API.get(`/analytics/${datasetId}/top-products`, { params }),
        API.get(`/analytics/${datasetId}/insights`, { params }),
        API.get(`/analytics/${datasetId}/filters`)
      ])
      setKpis(kpiRes.data); setTrend(trendRes.data); setRegions(regRes.data)
      setCategories(catRes.data); setTopProducts(prodRes.data); setInsights(insRes.data)
      setFilterOptions(filterRes.data)
    } catch (err) {
      toast.error('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }, [datasetId, filters])

  useEffect(() => { loadData() }, [loadData])

  const loadAdvanced = async () => {
    if (!datasetId) return
    try {
      const [anomRes, foreRes] = await Promise.all([
        API.get(`/analytics/${datasetId}/anomalies`),
        API.get(`/analytics/${datasetId}/forecast`)
      ])
      setAnomalies(anomRes.data); setForecast(foreRes.data)
    } catch {}
  }

  useEffect(() => {
    if (activeTab === 'advanced') loadAdvanced()
  }, [activeTab, datasetId])

  const exportCSV = () => {
    const token = localStorage.getItem('token')
    window.open(`/api/export/${datasetId}/csv?token=${token}`, '_blank')
  }
  const exportPDF = () => {
    const token = localStorage.getItem('token')
    window.open(`/api/export/${datasetId}/pdf?token=${token}`, '_blank')
  }

  if (datasets.length === 0) return (
    <div>
      <div className="page-header"><h2>Dashboard</h2></div>
      <div className="empty-state" style={{background:'#fff', borderRadius:10, padding:'3rem', boxShadow:'var(--shadow)'}}>
        <div className="icon">📊</div>
        <p style={{fontSize:'1rem', fontWeight:600, marginBottom:'.5rem'}}>No datasets available</p>
        <p style={{marginBottom:'1.5rem'}}>Upload a CSV or Excel file to get started</p>
        <button className="btn btn-primary" onClick={() => navigate('/upload')}>Upload Data</button>
      </div>
    </div>
  )

  const combinedTrend = [
    ...trend.map(t => ({...t, type: 'actual'})),
    ...forecast.map(f => ({month: f.month, predicted_sales: f.predicted_sales, type: 'forecast'}))
  ]

  return (
    <div>
      <div className="page-header" style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
        <div>
          <h2>Sales Dashboard</h2>
          <p>Real-time analytics and business intelligence</p>
        </div>
        {datasetId && (
          <div className="export-bar" style={{margin:0}}>
            <button className="btn btn-secondary btn-sm" onClick={exportCSV}><FiDownload size={14}/> CSV</button>
            <button className="btn btn-secondary btn-sm" onClick={exportPDF}><FiDownload size={14}/> PDF Report</button>
            <button className="btn btn-secondary btn-sm" onClick={loadData}><FiRefreshCw size={14}/></button>
          </div>
        )}
      </div>

      {/* Dataset selector */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>Dataset</label>
          <select value={datasetId || ''} onChange={e => setDatasetId(Number(e.target.value))}>
            {datasets.map(d => <option key={d.id} value={d.id}>{d.filename} ({d.row_count?.toLocaleString()} rows)</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>Region</label>
          <select value={filters.region} onChange={e => setFilters({...filters, region: e.target.value})}>
            <option value="">All Regions</option>
            {filterOptions.regions.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>Category</label>
          <select value={filters.category} onChange={e => setFilters({...filters, category: e.target.value})}>
            <option value="">All Categories</option>
            {filterOptions.categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>From</label>
          <input type="date" value={filters.date_from} onChange={e => setFilters({...filters, date_from: e.target.value})} />
        </div>
        <div className="filter-group">
          <label>To</label>
          <input type="date" value={filters.date_to} onChange={e => setFilters({...filters, date_to: e.target.value})} />
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => setFilters({ region: '', category: '', date_from: '', date_to: '' })}>
          Reset
        </button>
      </div>

      {/* Tabs */}
      <div className="section-tabs">
        {['overview', 'trends', 'products', 'insights', 'advanced'].map(tab => (
          <button key={tab} className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {loading && <Loading text="Loading analytics..." />}

      {!loading && activeTab === 'overview' && (
        <>
          {/* KPI Cards */}
          <div className="kpi-grid">
            <KpiCard label="Total Sales" value={fmt(kpis?.total_sales)} icon={<FiDollarSign />} color="blue" />
            <KpiCard label="Total Profit" value={fmt(kpis?.total_profit)} icon={<FiTrendingUp />} color="green" />
            <KpiCard label="Profit Margin" value={kpis ? `${kpis.profit_margin}%` : '—'} icon={<FiPercent />} color="purple" />
            <KpiCard label="Total Orders" value={kpis?.total_orders?.toLocaleString() || '—'} icon={<FiShoppingCart />} color="orange" />
            <KpiCard label="Avg Discount" value={kpis ? `${kpis.avg_discount}%` : '—'} icon={<FiTag />} color="red" />
          </div>

          {/* Charts Row 1 */}
          <div className="charts-grid">
            <div className="chart-card">
              <h3>Sales by Region</h3>
              {regions.length ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={regions}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="region" tick={{fontSize:12}} />
                    <YAxis tick={{fontSize:11}} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                    <Tooltip formatter={v => [`$${v.toLocaleString()}`, '']} />
                    <Legend />
                    <Bar dataKey="sales" fill="#2563eb" radius={[4,4,0,0]} name="Sales" />
                    <Bar dataKey="profit" fill="#16a34a" radius={[4,4,0,0]} name="Profit" />
                  </BarChart>
                </ResponsiveContainer>
              ) : <EmptyState />}
            </div>

            <div className="chart-card">
              <h3>Category Performance</h3>
              {categories.length ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={categories} dataKey="sales" nameKey="category"
                      cx="50%" cy="50%" outerRadius={90} label={({category, percent}) => `${category} ${(percent*100).toFixed(0)}%`}>
                      {categories.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={v => [`$${v.toLocaleString()}`, 'Sales']} />
                  </PieChart>
                </ResponsiveContainer>
              ) : <EmptyState />}
            </div>
          </div>

          {/* Category table */}
          <div className="table-card">
            <h3>Category Breakdown</h3>
            <table>
              <thead>
                <tr><th>Category</th><th>Sales</th><th>Profit</th><th>Margin</th></tr>
              </thead>
              <tbody>
                {categories.map(c => (
                  <tr key={c.category}>
                    <td><strong>{c.category}</strong></td>
                    <td>{fmt(c.sales)}</td>
                    <td style={{color: c.profit < 0 ? '#dc2626' : '#16a34a'}}>{fmt(c.profit)}</td>
                    <td>
                      <span className={`badge ${c.margin > 15 ? 'badge-green' : c.margin > 5 ? 'badge-blue' : 'badge-red'}`}>
                        {c.margin.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!loading && activeTab === 'trends' && (
        <>
          <div className="chart-card" style={{marginBottom:'1.25rem'}}>
            <h3>Monthly Sales & Profit Trend</h3>
            {trend.length ? (
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={trend}>
                  <defs>
                    <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#16a34a" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{fontSize:11}} />
                  <YAxis tick={{fontSize:11}} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                  <Tooltip formatter={v => [`$${v.toLocaleString()}`, '']} />
                  <Legend />
                  <Area type="monotone" dataKey="sales" stroke="#2563eb" fill="url(#salesGrad)" strokeWidth={2} name="Sales" />
                  <Area type="monotone" dataKey="profit" stroke="#16a34a" fill="url(#profitGrad)" strokeWidth={2} name="Profit" />
                </AreaChart>
              </ResponsiveContainer>
            ) : <EmptyState />}
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Region Sales Distribution</h3>
              {regions.length ? (
                <ResponsiveContainer width="100%" height={260}>
                  <RadarChart data={regions}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="region" tick={{fontSize:12}} />
                    <Radar name="Sales" dataKey="sales" stroke="#2563eb" fill="#2563eb" fillOpacity={0.3} />
                    <Radar name="Profit" dataKey="profit" stroke="#16a34a" fill="#16a34a" fillOpacity={0.3} />
                    <Legend />
                    <Tooltip formatter={v => [`$${v.toLocaleString()}`, '']} />
                  </RadarChart>
                </ResponsiveContainer>
              ) : <EmptyState />}
            </div>
            <div className="chart-card">
              <h3>Category Profit Margin</h3>
              {categories.length ? (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={categories} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis type="number" tick={{fontSize:11}} tickFormatter={v => `${v}%`} />
                    <YAxis dataKey="category" type="category" tick={{fontSize:12}} width={120} />
                    <Tooltip formatter={v => [`${v}%`, 'Margin']} />
                    <Bar dataKey="margin" fill="#7c3aed" radius={[0,4,4,0]} name="Profit Margin" />
                  </BarChart>
                </ResponsiveContainer>
              ) : <EmptyState />}
            </div>
          </div>
        </>
      )}

      {!loading && activeTab === 'products' && (
        <>
          <div className="chart-card" style={{marginBottom:'1.25rem'}}>
            <h3>Top 5 Products by Sales</h3>
            {topProducts.length ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={topProducts} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" tick={{fontSize:11}} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                  <YAxis dataKey="product" type="category" tick={{fontSize:11}} width={200} />
                  <Tooltip formatter={v => [`$${v.toLocaleString()}`, 'Sales']} />
                  <Bar dataKey="sales" radius={[0,4,4,0]} name="Sales">
                    {topProducts.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : <EmptyState />}
          </div>

          <div className="table-card">
            <h3>Top Products Ranking</h3>
            <table>
              <thead><tr><th>#</th><th>Product</th><th>Sales</th></tr></thead>
              <tbody>
                {topProducts.map((p, i) => (
                  <tr key={i}>
                    <td><span className="badge badge-blue">#{i + 1}</span></td>
                    <td>{p.product}</td>
                    <td><strong>{fmt(p.sales)}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {!loading && activeTab === 'insights' && (
        <>
          <div className="insights-panel">
            <h3>💡 Auto-Generated Insights</h3>
            {insights.length === 0 ? <EmptyState icon="💡" message="No insights available" /> :
              insights.map((ins, i) => (
                <div key={i} className="insight-item">
                  <div className="insight-icon">💡</div>
                  <div className="insight-text">{ins}</div>
                </div>
              ))
            }
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Profit vs Sales by Category</h3>
              {categories.length ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={categories}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="category" tick={{fontSize:11}} />
                    <YAxis tick={{fontSize:11}} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                    <Tooltip formatter={v => [`$${v.toLocaleString()}`, '']} />
                    <Legend />
                    <Bar dataKey="sales" fill="#2563eb" name="Sales" radius={[4,4,0,0]} />
                    <Bar dataKey="profit" fill="#16a34a" name="Profit" radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : <EmptyState />}
            </div>
            <div className="chart-card">
              <h3>Sales Summary</h3>
              {kpis && (
                <div style={{padding:'1rem'}}>
                  {[
                    {label: 'Total Revenue', value: fmt(kpis.total_sales), color: '#2563eb'},
                    {label: 'Total Profit', value: fmt(kpis.total_profit), color: '#16a34a'},
                    {label: 'Profit Margin', value: `${kpis.profit_margin}%`, color: '#7c3aed'},
                    {label: 'Avg Discount', value: `${kpis.avg_discount}%`, color: '#d97706'},
                    {label: 'Total Orders', value: kpis.total_orders?.toLocaleString(), color: '#0891b2'},
                  ].map(({label, value, color}) => (
                    <div key={label} style={{display:'flex', justifyContent:'space-between',
                      padding:'.75rem 0', borderBottom:'1px solid #f1f5f9'}}>
                      <span style={{color:'#64748b', fontSize:'.875rem'}}>{label}</span>
                      <strong style={{color, fontSize:'.95rem'}}>{value}</strong>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {!loading && activeTab === 'advanced' && (
        <>
          <div className="chart-card" style={{marginBottom:'1.25rem'}}>
            <h3>📈 Sales Forecast (Next 3 Months)</h3>
            {forecast.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={[...trend.slice(-6), ...forecast.map(f => ({month: f.month, predicted_sales: f.predicted_sales}))]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{fontSize:11}} />
                  <YAxis tick={{fontSize:11}} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                  <Tooltip formatter={v => [`$${v?.toLocaleString()}`, '']} />
                  <Legend />
                  <Line type="monotone" dataKey="sales" stroke="#2563eb" strokeWidth={2} name="Actual Sales" dot={false} />
                  <Line type="monotone" dataKey="predicted_sales" stroke="#d97706" strokeWidth={2}
                    strokeDasharray="6 3" name="Forecast" dot={{fill:'#d97706'}} />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyState icon="📈" message="Loading forecast..." />}
            {forecast.length > 0 && (
              <div style={{display:'flex', gap:'1rem', marginTop:'1rem', flexWrap:'wrap'}}>
                {forecast.map(f => (
                  <div key={f.month} style={{background:'rgba(217,119,6,.08)', borderRadius:8,
                    padding:'.75rem 1rem', flex:'1', minWidth:140}}>
                    <div style={{color:'#d97706', fontWeight:600, fontSize:'.8rem'}}>{f.month}</div>
                    <div style={{fontSize:'1.2rem', fontWeight:700, marginTop:'.25rem'}}>{fmt(f.predicted_sales)}</div>
                    <div style={{color:'#64748b', fontSize:'.75rem'}}>Forecast</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="table-card">
            <h3><FiAlertTriangle style={{display:'inline', color:'#dc2626', marginRight:'.5rem'}} />
              Sales Anomalies (2.5σ threshold)</h3>
            {anomalies.length === 0 ? (
              <div className="empty-state"><div className="icon">✅</div><p>No significant anomalies detected</p></div>
            ) : (
              <table>
                <thead><tr><th>Order ID</th><th>Product</th><th>Sales</th><th>Date</th></tr></thead>
                <tbody>
                  {anomalies.map((a, i) => (
                    <tr key={i}>
                      <td><code style={{fontSize:'.8rem'}}>{a.order_id}</code></td>
                      <td>{a.product}</td>
                      <td><span className="anomaly-badge">{fmt(a.sales)}</span></td>
                      <td>{a.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  )
}
