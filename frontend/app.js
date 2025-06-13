const { useState, useEffect } = React;

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [teams, setTeams] = useState([]);
  const [teamName, setTeamName] = useState('');

  const api = (path, opts = {}) => {
    opts.headers = opts.headers || {};
    if (token) opts.headers['Authorization'] = 'Bearer ' + token;
    return fetch(path, opts).then(r => r.json());
  };

  const login = () => {
    api('/users/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    }).then(data => {
      if (data.token) {
        localStorage.setItem('token', data.token);
        setToken(data.token);
      } else {
        alert(data.detail || 'Login failed');
      }
    });
  };

  const register = () => {
    api('/users/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    }).then(data => {
      if (data.id) {
        alert('Registered');
      } else {
        alert(data.detail || 'Failed');
      }
    });
  };

  const loadTeams = () => {
    api('/teams').then(data => setTeams(data));
  };

  const createTeam = () => {
    api('/teams?name=' + encodeURIComponent(teamName), { method: 'POST' }).then(
      data => {
        if (data.team_id) {
          setTeamName('');
          loadTeams();
        } else {
          alert(data.detail || 'Failed');
        }
      }
    );
  };

  useEffect(() => {
    if (token) loadTeams();
  }, [token]);

  if (!token) {
    return (
      <div>
        <h2>Login / Register</h2>
        <input
          placeholder="username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
        <input
          placeholder="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        <button onClick={login}>Login</button>
        <button onClick={register}>Register</button>
      </div>
    );
  }

  return (
    <div>
      <h2>Teams</h2>
      <ul>
        {teams.map(t => (
          <li key={t.id}>{t.name} ({t.role})</li>
        ))}
      </ul>
      <input
        placeholder="new team"
        value={teamName}
        onChange={e => setTeamName(e.target.value)}
      />
      <button onClick={createTeam}>Create Team</button>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
