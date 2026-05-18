"""Browser-based interface for the student database system."""

from __future__ import annotations

import http.server
import json
import socketserver
import webbrowser
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from student_database.constants import (
    ALLOWED_PARENT_RELATIONSHIPS,
    ALLOWED_STATUSES,
    DEFAULT_DATA_PATH,
    DEFAULT_EXPORT_PATH,
    YEAR_LEVELS,
)
from student_database.manager import StudentManager
from student_database.models import Parent, Student, attendance_label
from student_database.reports import BasicReport, DetailedReport


APP_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Student Database System</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">SD</div>
        <div>
          <div class="brand-title">Student Database</div>
          <div class="brand-subtitle">Management Console</div>
        </div>
      </div>
      <nav class="nav" aria-label="Main navigation">
        <button class="nav-button active" data-screen="students">View / Search</button>
        <button class="nav-button" data-screen="add">Add Student</button>
        <button class="nav-button" data-screen="update">Update / Delete</button>
        <button class="nav-button" data-screen="grades">Grades & Attendance</button>
        <button class="nav-button" data-screen="parents">Parents / Guardians</button>
        <button class="nav-button" data-screen="reports">Reports</button>
        <button class="nav-button" data-screen="storage">Save / Export</button>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <div>
          <h1 id="screen-title">View / Search Students</h1>
          <p id="status-line">Ready</p>
        </div>
        <div class="quick-stats" id="quick-stats"></div>
      </header>
      <section id="app" class="app" aria-live="polite"></section>
    </main>
  </div>
  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <script src="/app.js"></script>
</body>
</html>
"""


APP_CSS = r"""
:root {
  --bg: #f6f5f0;
  --panel: #ffffff;
  --panel-soft: #fbfaf6;
  --ink: #1f2933;
  --muted: #667085;
  --line: #d8ded9;
  --teal: #126e72;
  --teal-dark: #0c4f53;
  --coral: #c7553f;
  --amber: #b7791f;
  --green: #277344;
  --red: #aa3333;
  --shadow: 0 18px 38px rgba(31, 41, 51, 0.10);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
}

button,
input,
select,
textarea {
  font: inherit;
}

.shell {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  background: #17343a;
  color: #f7faf8;
  padding: 22px 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #17343a;
  background: #f0c674;
  font-weight: 800;
}

.brand-title {
  font-size: 17px;
  font-weight: 800;
}

.brand-subtitle {
  margin-top: 2px;
  color: #bfd0ca;
  font-size: 13px;
}

.nav {
  display: grid;
  gap: 6px;
}

.nav-button {
  width: 100%;
  border: 0;
  border-radius: 8px;
  color: #ecf4f1;
  background: transparent;
  padding: 11px 12px;
  text-align: left;
  cursor: pointer;
}

.nav-button:hover,
.nav-button:focus-visible {
  outline: none;
  background: rgba(255, 255, 255, 0.10);
}

.nav-button.active {
  background: #f7faf8;
  color: #17343a;
  font-weight: 800;
}

.main {
  min-width: 0;
  padding: 24px;
}

.topbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
}

#status-line {
  margin: 6px 0 0;
  color: var(--muted);
}

.quick-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stat {
  min-width: 112px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px 11px;
  box-shadow: 0 8px 20px rgba(31, 41, 51, 0.05);
}

.stat-value {
  font-size: 20px;
  font-weight: 800;
}

.stat-label {
  margin-top: 2px;
  color: var(--muted);
  font-size: 12px;
}

.app {
  min-height: calc(100vh - 126px);
}

.toolbar,
.actions,
.form-actions {
  display: flex;
  align-items: end;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  box-shadow: var(--shadow);
}

.field {
  display: grid;
  gap: 5px;
  min-width: 150px;
}

.field.grow {
  flex: 1 1 240px;
}

label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #cfd7d3;
  border-radius: 7px;
  background: #fff;
  color: var(--ink);
  padding: 10px 11px;
}

textarea {
  min-height: 240px;
  resize: vertical;
}

input:focus,
select:focus,
textarea:focus {
  outline: 3px solid rgba(18, 110, 114, 0.18);
  border-color: var(--teal);
}

button {
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 10px 13px;
  cursor: pointer;
  background: var(--teal);
  color: #fff;
  font-weight: 800;
}

button:hover {
  background: var(--teal-dark);
}

button:disabled,
button:disabled:hover {
  background: #c5ceca;
  color: #5d6964;
  cursor: not-allowed;
}

button.secondary {
  background: #fff;
  color: var(--ink);
  border-color: #cfd7d3;
}

button.secondary:hover {
  background: #f0f4f2;
}

button.danger {
  background: var(--red);
}

button.danger:hover {
  background: #842525;
}

.grid-2 {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(340px, 0.46fr);
  gap: 16px;
  margin-top: 16px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
  min-width: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--line);
  padding: 13px 14px;
}

.panel-title {
  font-size: 15px;
  font-weight: 900;
}

.panel-body {
  padding: 14px;
}

.table-wrap {
  overflow: auto;
  max-height: calc(100vh - 290px);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th {
  position: sticky;
  top: 0;
  z-index: 1;
  color: #415056;
  background: #eef2ef;
  text-align: left;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0;
}

th,
td {
  border-bottom: 1px solid #e6ebe7;
  padding: 10px;
  vertical-align: top;
}

tbody tr {
  cursor: pointer;
}

tbody tr:hover,
tbody tr.selected {
  background: #edf8f6;
}

.pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  border-radius: 999px;
  padding: 3px 9px;
  background: #edf2f0;
  color: #344347;
  font-size: 12px;
  font-weight: 800;
}

.pill.Active {
  background: #e5f5e9;
  color: var(--green);
}

.pill.Inactive,
.pill.Suspended {
  background: #f9e7e4;
  color: var(--red);
}

.pill.Graduated {
  background: #fff2d8;
  color: var(--amber);
}

.detail {
  white-space: pre-wrap;
  line-height: 1.5;
}

.empty {
  color: var(--muted);
  padding: 20px;
  text-align: center;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 13px;
}

.full {
  grid-column: 1 / -1;
}

.stack {
  display: grid;
  gap: 16px;
}

.mini-table {
  margin-top: 10px;
  max-height: 240px;
  overflow: auto;
  border: 1px solid #e1e7e3;
  border-radius: 8px;
}

.split-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.toast {
  position: fixed;
  right: 18px;
  bottom: 18px;
  max-width: 420px;
  border-radius: 8px;
  background: var(--ink);
  color: #fff;
  padding: 12px 14px;
  box-shadow: var(--shadow);
  opacity: 0;
  transform: translateY(8px);
  pointer-events: none;
  transition: opacity 160ms ease, transform 160ms ease;
}

.toast.show {
  opacity: 1;
  transform: translateY(0);
}

.toast.error {
  background: var(--red);
}

@media (max-width: 940px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: sticky;
    top: 0;
    z-index: 5;
  }

  .nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .topbar,
  .grid-2 {
    display: block;
  }

  .quick-stats,
  .grid-2 > * + * {
    margin-top: 14px;
  }
}

@media (max-width: 620px) {
  .main {
    padding: 14px;
  }

  .form-grid,
  .nav {
    grid-template-columns: 1fr;
  }

  .toolbar,
  .actions,
  .form-actions {
    align-items: stretch;
  }
}
"""


APP_JS = r"""
const app = document.querySelector("#app");
const title = document.querySelector("#screen-title");
const statusLine = document.querySelector("#status-line");
const quickStats = document.querySelector("#quick-stats");
const toast = document.querySelector("#toast");

let options = {
  statuses: [],
  year_levels: [],
  relationships: []
};
let currentStudentId = null;
let pendingParents = [];

const screens = {
  students: renderStudents,
  add: renderAddStudent,
  update: () => renderUpdateDelete(),
  grades: renderGradesAttendance,
  parents: renderParents,
  reports: renderReports,
  storage: renderStorage
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusPill(status) {
  return `<span class="pill ${escapeHtml(status)}">${escapeHtml(status)}</span>`;
}

function setTitle(text) {
  title.textContent = text;
}

function setStatus(text) {
  statusLine.textContent = text;
}

function setActive(screen) {
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.screen === screen);
  });
}

function showToast(message, kind = "ok") {
  toast.textContent = message;
  toast.classList.toggle("error", kind === "error");
  toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2800);
}

async function api(path, config = {}) {
  const headers = {"Accept": "application/json", ...(config.headers || {})};
  if (config.body && !(config.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(path, {...config, headers});
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) {
    throw new Error(payload.error || response.statusText || "Request failed");
  }
  return payload;
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function optionTags(values, selected = "") {
  return values
    .map((value) => {
      const text = String(value);
      const isSelected = text === String(selected) ? " selected" : "";
      return `<option value="${escapeHtml(text)}"${isSelected}>${escapeHtml(text)}</option>`;
    })
    .join("");
}

function renderQuickStats(state = {}) {
  quickStats.innerHTML = `
    <div class="stat">
      <div class="stat-value">${escapeHtml(state.count ?? 0)}</div>
      <div class="stat-label">Students</div>
    </div>
    <div class="stat">
      <div class="stat-value">${escapeHtml(Number(state.average_class_gpa ?? 0).toFixed(2))}</div>
      <div class="stat-label">Class GPA</div>
    </div>
  `;
}

function studentRows(students) {
  if (!students.length) {
    return `<tr><td colspan="9" class="empty">No students found.</td></tr>`;
  }
  return students.map((student) => `
    <tr data-id="${escapeHtml(student.student_id)}">
      <td>${escapeHtml(student.student_id)}</td>
      <td>${escapeHtml(student.name)}</td>
      <td>${escapeHtml(student.major)}</td>
      <td>${escapeHtml(student.year_level)}</td>
      <td>${escapeHtml(student.gpa.toFixed(2))}</td>
      <td>${escapeHtml(student.average_grade.toFixed(2))}</td>
      <td>${escapeHtml(student.attendance_percentage.toFixed(2))}%</td>
      <td>${statusPill(student.status)}</td>
      <td>${escapeHtml(student.category)}</td>
    </tr>
  `).join("");
}

function studentsTable(students) {
  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Major</th>
            <th>Year</th>
            <th>GPA</th>
            <th>Average</th>
            <th>Attendance</th>
            <th>Status</th>
            <th>Category</th>
          </tr>
        </thead>
        <tbody>${studentRows(students)}</tbody>
      </table>
    </div>
  `;
}

async function loadStudentDetail(studentId, detailTarget = "#student-detail") {
  const detail = document.querySelector(detailTarget);
  if (!detail) return;
  try {
    const payload = await api(`/api/students/${encodeURIComponent(studentId)}`);
    currentStudentId = payload.student.student_id;
    detail.innerHTML = `
      <div class="panel-header">
        <div class="panel-title">${escapeHtml(payload.student.name)}</div>
        <span class="pill">${escapeHtml(payload.student.student_id)}</span>
      </div>
      <div class="panel-body detail">${escapeHtml(payload.detail_text)}</div>
      <div class="panel-body split-actions">
        <button type="button" id="edit-selected">Edit</button>
        <button type="button" class="danger" id="delete-selected">Delete</button>
      </div>
    `;
    document.querySelector("#edit-selected").addEventListener("click", () => {
      renderUpdateDelete(currentStudentId);
    });
    document.querySelector("#delete-selected").addEventListener("click", async () => {
      if (!window.confirm(`Delete ${payload.student.name} (${payload.student.student_id})?`)) return;
      try {
        await api(`/api/students/${encodeURIComponent(payload.student.student_id)}`, {method: "DELETE"});
        showToast("Student deleted.");
        await renderStudents();
      } catch (error) {
        showToast(error.message, "error");
      }
    });
  } catch (error) {
    detail.innerHTML = `<div class="panel-body empty">${escapeHtml(error.message)}</div>`;
  }
}

async function renderStudents() {
  setActive("students");
  setTitle("View / Search Students");
  setStatus("Loading student records...");
  app.innerHTML = `
    <div class="toolbar">
      <div class="field grow">
        <label for="search">Search</label>
        <input id="search" name="search" type="search" placeholder="ID, name, or major">
      </div>
      <div class="field">
        <label for="filter-type">Filter</label>
        <select id="filter-type">
          <option value="all">All</option>
          <option value="major">Major</option>
          <option value="year">Year Level</option>
          <option value="status">Status</option>
        </select>
      </div>
      <div class="field">
        <label for="filter-value">Value</label>
        <select id="filter-value" disabled></select>
      </div>
      <button type="button" id="apply-filter">Apply</button>
      <button type="button" class="secondary" id="clear-filter">Refresh</button>
      <button type="button" id="new-student">Add Student</button>
    </div>
    <div class="grid-2">
      <section class="panel" id="student-table-panel">
        <div class="panel-header">
          <div class="panel-title">Student Records</div>
          <span class="pill" id="majors-pill">Majors</span>
        </div>
        <div id="students-table"></div>
      </section>
      <aside class="panel" id="student-detail">
        <div class="panel-body empty">Select a student to view details.</div>
      </aside>
    </div>
  `;

  const search = document.querySelector("#search");
  const filterType = document.querySelector("#filter-type");
  const filterValue = document.querySelector("#filter-value");
  const tableTarget = document.querySelector("#students-table");
  const majorsPill = document.querySelector("#majors-pill");

  function setFilterOptions() {
    const type = filterType.value;
    if (type === "major") {
      filterValue.innerHTML = optionTags(window.lastMajors || []);
      filterValue.disabled = false;
    } else if (type === "year") {
      filterValue.innerHTML = optionTags(options.year_levels);
      filterValue.disabled = false;
    } else if (type === "status") {
      filterValue.innerHTML = optionTags(options.statuses);
      filterValue.disabled = false;
    } else {
      filterValue.innerHTML = "";
      filterValue.disabled = true;
    }
  }

  async function loadList(params = {}) {
    const query = new URLSearchParams(params).toString();
    const state = await api(`/api/students${query ? `?${query}` : ""}`);
    window.lastMajors = state.majors;
    tableTarget.innerHTML = studentsTable(state.students);
    majorsPill.textContent = state.majors.length ? `Majors: ${state.majors.join(", ")}` : "No majors";
    renderQuickStats(state);
    setFilterOptions();
    setStatus(`Showing ${state.students.length} student(s).`);
    tableTarget.querySelectorAll("tbody tr[data-id]").forEach((row) => {
      row.addEventListener("click", () => {
        tableTarget.querySelectorAll("tr").forEach((item) => item.classList.remove("selected"));
        row.classList.add("selected");
        loadStudentDetail(row.dataset.id);
      });
    });
  }

  document.querySelector("#apply-filter").addEventListener("click", async () => {
    try {
      const params = {};
      if (search.value.trim()) params.search = search.value.trim();
      if (filterType.value !== "all") {
        params.filter_type = filterType.value;
        params.filter_value = filterValue.value;
      }
      await loadList(params);
    } catch (error) {
      showToast(error.message, "error");
    }
  });
  document.querySelector("#clear-filter").addEventListener("click", () => renderStudents());
  document.querySelector("#new-student").addEventListener("click", renderAddStudent);
  search.addEventListener("keydown", (event) => {
    if (event.key === "Enter") document.querySelector("#apply-filter").click();
  });
  filterType.addEventListener("change", setFilterOptions);

  try {
    await loadList();
  } catch (error) {
    showToast(error.message, "error");
    setStatus(error.message);
  }
}

function parentRows(parents, removable = false) {
  if (!parents.length) {
    return `<tr><td colspan="${removable ? 5 : 4}" class="empty">No parents found.</td></tr>`;
  }
  return parents.map((parent, index) => `
    <tr data-index="${index}">
      <td>${escapeHtml(parent.name)}</td>
      <td>${escapeHtml(parent.relationship)}</td>
      <td>${escapeHtml(parent.email)}</td>
      <td>${escapeHtml(parent.phone)}</td>
      ${removable ? `<td><button type="button" class="secondary parent-remove" data-index="${index}">Remove</button></td>` : ""}
    </tr>
  `).join("");
}

function parentTable(parents, removable = false) {
  return `
    <div class="mini-table">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Relationship</th>
            <th>Email</th>
            <th>Phone</th>
            ${removable ? "<th>Action</th>" : ""}
          </tr>
        </thead>
        <tbody>${parentRows(parents, removable)}</tbody>
      </table>
    </div>
  `;
}

function renderPendingParents() {
  const target = document.querySelector("#pending-parent-table");
  if (!target) return;
  target.innerHTML = parentTable(pendingParents, true);
  target.querySelectorAll(".parent-remove").forEach((button) => {
    button.addEventListener("click", () => {
      pendingParents.splice(Number(button.dataset.index), 1);
      renderPendingParents();
    });
  });
}

function parentForm(prefix) {
  return `
    <div class="form-grid">
      <div class="field">
        <label for="${prefix}-parent-name">Name</label>
        <input id="${prefix}-parent-name" name="name" required>
      </div>
      <div class="field">
        <label for="${prefix}-relationship">Relationship</label>
        <select id="${prefix}-relationship" name="relationship">${optionTags(options.relationships)}</select>
      </div>
      <div class="field">
        <label for="${prefix}-parent-email">Email</label>
        <input id="${prefix}-parent-email" name="email" type="email" required>
      </div>
      <div class="field">
        <label for="${prefix}-parent-phone">Phone</label>
        <input id="${prefix}-parent-phone" name="phone" required>
      </div>
    </div>
  `;
}

function renderAddStudent() {
  setActive("add");
  setTitle("Add New Student");
  setStatus("Ready");
  pendingParents = [];
  app.innerHTML = `
    <div class="grid-2">
      <section class="panel">
        <div class="panel-header"><div class="panel-title">Student Information</div></div>
        <div class="panel-body">
          <form id="student-create-form" class="stack">
            <div class="form-grid">
              <div class="field">
                <label for="student-id">Student ID</label>
                <input id="student-id" name="student_id" required>
              </div>
              <div class="field">
                <label for="student-name">Name</label>
                <input id="student-name" name="name" required>
              </div>
              <div class="field">
                <label for="student-age">Age</label>
                <input id="student-age" name="age" type="number" min="15" max="100" required>
              </div>
              <div class="field">
                <label for="student-email">Email</label>
                <input id="student-email" name="email" type="email" required>
              </div>
              <div class="field">
                <label for="student-phone">Phone</label>
                <input id="student-phone" name="phone" required>
              </div>
              <div class="field">
                <label for="student-major">Major</label>
                <input id="student-major" name="major" required>
              </div>
              <div class="field">
                <label for="student-year">Year Level</label>
                <select id="student-year" name="year_level">${optionTags(options.year_levels)}</select>
              </div>
              <div class="field">
                <label for="student-status">Status</label>
                <select id="student-status" name="status">${optionTags(options.statuses)}</select>
              </div>
            </div>
            <div class="form-actions">
              <button type="submit">Save Student</button>
              <button type="reset" class="secondary">Clear</button>
            </div>
          </form>
        </div>
      </section>
      <aside class="panel">
        <div class="panel-header"><div class="panel-title">Parent / Guardian Contacts</div></div>
        <div class="panel-body stack">
          <form id="pending-parent-form" class="stack">
            ${parentForm("pending")}
            <div class="form-actions">
              <button type="submit" class="secondary">Add Parent</button>
            </div>
          </form>
          <div id="pending-parent-table"></div>
        </div>
      </aside>
    </div>
  `;
  renderPendingParents();

  document.querySelector("#pending-parent-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    pendingParents.push(formData(form));
    form.reset();
    document.querySelector("#pending-relationship").value = options.relationships[0] || "";
    renderPendingParents();
    showToast("Parent added to form.");
  });

  document.querySelector("#student-create-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {...formData(form), parents: pendingParents};
    try {
      await api("/api/students", {method: "POST", body: JSON.stringify(payload)});
      showToast("Student added.");
      renderStudents();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

async function renderUpdateDelete(prefillId = "") {
  setActive("update");
  setTitle("Update / Delete Student");
  setStatus("Ready");
  app.innerHTML = `
    <div class="toolbar">
      <div class="field grow">
        <label for="lookup-id">Student ID</label>
        <input id="lookup-id" value="${escapeHtml(prefillId)}">
      </div>
      <button type="button" id="load-student">Load</button>
      <button type="button" class="secondary" id="back-to-list">Back to List</button>
    </div>
    <div class="grid-2">
      <section class="panel">
        <div class="panel-header"><div class="panel-title">Editable Fields</div></div>
        <div class="panel-body">
          <form id="update-form" class="stack">
            <div class="form-grid">
              <div class="field">
                <label for="update-name">Name</label>
                <input id="update-name" name="name" required>
              </div>
              <div class="field">
                <label for="update-age">Age</label>
                <input id="update-age" name="age" type="number" min="15" max="100" required>
              </div>
              <div class="field">
                <label for="update-email">Email</label>
                <input id="update-email" name="email" type="email" required>
              </div>
              <div class="field">
                <label for="update-phone">Phone</label>
                <input id="update-phone" name="phone" required>
              </div>
              <div class="field">
                <label for="update-major">Major</label>
                <input id="update-major" name="major" required>
              </div>
              <div class="field">
                <label for="update-year">Year Level</label>
                <select id="update-year" name="year_level">${optionTags(options.year_levels)}</select>
              </div>
              <div class="field">
                <label for="update-status">Status</label>
                <select id="update-status" name="status">${optionTags(options.statuses)}</select>
              </div>
            </div>
            <div class="split-actions">
              <div class="form-actions">
                <button type="submit">Save Updates</button>
                <button type="button" class="danger" id="delete-loaded">Delete Student</button>
              </div>
            </div>
          </form>
        </div>
      </section>
      <aside class="panel" id="loaded-detail">
        <div class="panel-body empty">Load a student to edit.</div>
      </aside>
    </div>
  `;

  const lookup = document.querySelector("#lookup-id");
  const form = document.querySelector("#update-form");
  const detail = document.querySelector("#loaded-detail");
  let loadedId = "";

  async function loadStudent() {
    try {
      const payload = await api(`/api/students/${encodeURIComponent(lookup.value.trim())}`);
      const student = payload.student;
      loadedId = student.student_id;
      form.elements.name.value = student.name;
      form.elements.age.value = student.age;
      form.elements.email.value = student.email;
      form.elements.phone.value = student.phone;
      form.elements.major.value = student.major;
      form.elements.year_level.value = String(student.year_level);
      form.elements.status.value = student.status;
      detail.innerHTML = `<div class="panel-body detail">${escapeHtml(payload.detail_text)}</div>`;
      setStatus(`Loaded ${student.name}.`);
    } catch (error) {
      showToast(error.message, "error");
    }
  }

  document.querySelector("#load-student").addEventListener("click", loadStudent);
  document.querySelector("#back-to-list").addEventListener("click", renderStudents);
  lookup.addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadStudent();
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!loadedId) {
      showToast("Load a student first.", "error");
      return;
    }
    try {
      await api(`/api/students/${encodeURIComponent(loadedId)}`, {
        method: "PATCH",
        body: JSON.stringify(formData(form))
      });
      showToast("Student updated.");
      await loadStudent();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
  document.querySelector("#delete-loaded").addEventListener("click", async () => {
    if (!loadedId) {
      showToast("Load a student first.", "error");
      return;
    }
    if (!window.confirm(`Delete student ${loadedId}?`)) return;
    try {
      await api(`/api/students/${encodeURIComponent(loadedId)}`, {method: "DELETE"});
      showToast("Student deleted.");
      renderStudents();
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  if (prefillId) await loadStudent();
}

async function renderGradesAttendance() {
  setActive("grades");
  setTitle("Grades & Attendance");
  setStatus("Loading students...");
  app.innerHTML = `
    <div class="toolbar">
      <div class="field grow">
        <label for="ga-student">Student</label>
        <select id="ga-student"></select>
      </div>
      <button type="button" id="ga-load">Load</button>
    </div>
    <div class="grid-2">
      <section class="panel">
        <div class="panel-header"><div class="panel-title">Academic Records</div></div>
        <div class="panel-body stack">
          <form id="grade-form" class="stack">
            <div class="field">
              <label for="grade-score">Grade (0-100)</label>
              <input id="grade-score" name="grade" type="number" min="0" max="100" step="0.01" required>
            </div>
            <button type="submit" id="grade-submit" disabled>Add Grade</button>
          </form>
          <form id="attendance-form" class="stack">
            <div class="form-grid">
              <div class="field">
                <label for="attendance-present">Attendance</label>
                <select id="attendance-present" name="present">
                  <option value="true">Present</option>
                  <option value="false">Absent</option>
                </select>
              </div>
              <div class="field">
                <label for="attendance-date">Date</label>
                <input id="attendance-date" name="date" type="date">
              </div>
            </div>
            <button type="submit" id="attendance-submit" disabled>Record Attendance</button>
          </form>
        </div>
      </section>
      <aside class="panel" id="ga-detail">
        <div class="panel-body empty">Load a student to view records.</div>
      </aside>
    </div>
  `;

  const studentSelect = document.querySelector("#ga-student");
  const detail = document.querySelector("#ga-detail");
  const gradeSubmit = document.querySelector("#grade-submit");
  const attendanceSubmit = document.querySelector("#attendance-submit");
  let loadedId = "";

  function setRecordActionsEnabled(enabled) {
    gradeSubmit.disabled = !enabled;
    attendanceSubmit.disabled = !enabled;
  }

  async function loadDetail() {
    const selectedId = studentSelect.value;
    if (!selectedId) {
      loadedId = "";
      setRecordActionsEnabled(false);
      detail.innerHTML = `<div class="panel-body empty">Select a student to add records.</div>`;
      setStatus("No student selected.");
      return;
    }
    try {
      const payload = await api(`/api/students/${encodeURIComponent(selectedId)}`);
      const student = payload.student;
      loadedId = student.student_id;
      setRecordActionsEnabled(true);
      const gradeText = student.grades.length ? student.grades.map((grade) => grade.toFixed(1)).join(", ") : "No grades recorded";
      const attendanceText = student.attendance.length
        ? student.attendance.map((record) => `${record.date}: ${record.label}`).join("\n")
        : "No attendance recorded";
      detail.innerHTML = `
        <div class="panel-header">
          <div class="panel-title">${escapeHtml(student.name)}</div>
          <span class="pill">${escapeHtml(student.student_id)}</span>
        </div>
        <div class="panel-body detail">${escapeHtml(
          `Average Grade: ${student.average_grade.toFixed(2)}\nGPA: ${student.gpa.toFixed(2)}\nAttendance: ${student.attendance_percentage.toFixed(2)}%\n\nGrades:\n${gradeText}\n\nAttendance Records:\n${attendanceText}`
        )}</div>
      `;
      setStatus(`Loaded grades and attendance for ${student.name}.`);
    } catch (error) {
      loadedId = "";
      setRecordActionsEnabled(false);
      showToast(error.message, "error");
    }
  }

  async function loadStudentChoices() {
    try {
      const state = await api("/api/students");
      renderQuickStats(state);
      studentSelect.innerHTML = state.students.length
        ? state.students.map((student) => (
            `<option value="${escapeHtml(student.student_id)}">${escapeHtml(student.student_id)} - ${escapeHtml(student.name)}</option>`
          )).join("")
        : `<option value="">No students found</option>`;
      studentSelect.disabled = !state.students.length;
      setRecordActionsEnabled(false);
      if (state.students.length) {
        await loadDetail();
      } else {
        detail.innerHTML = `<div class="panel-body empty">Add a student before recording grades or attendance.</div>`;
        setStatus("No students found.");
      }
    } catch (error) {
      showToast(error.message, "error");
      setStatus(error.message);
    }
  }

  document.querySelector("#ga-load").addEventListener("click", loadDetail);
  studentSelect.addEventListener("change", loadDetail);
  document.querySelector("#grade-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!loadedId) {
      showToast("Select and load a student first.", "error");
      return;
    }
    try {
      await api(`/api/students/${encodeURIComponent(loadedId)}/grades`, {
        method: "POST",
        body: JSON.stringify(formData(form))
      });
      form.reset();
      showToast("Grade added.");
      await loadDetail();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
  document.querySelector("#attendance-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!loadedId) {
      showToast("Select and load a student first.", "error");
      return;
    }
    const payload = formData(form);
    payload.present = payload.present === "true";
    try {
      await api(`/api/students/${encodeURIComponent(loadedId)}/attendance`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      form.reset();
      showToast("Attendance recorded.");
      await loadDetail();
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  await loadStudentChoices();
}

function renderParents() {
  setActive("parents");
  setTitle("Parents / Guardians");
  setStatus("Ready");
  app.innerHTML = `
    <div class="toolbar">
      <div class="field grow">
        <label for="parents-id">Student ID</label>
        <input id="parents-id">
      </div>
      <button type="button" id="parents-load">Load</button>
    </div>
    <div class="grid-2">
      <section class="panel" id="parents-list">
        <div class="panel-body empty">Load a student to view parents.</div>
      </section>
      <aside class="panel">
        <div class="panel-header"><div class="panel-title">Add Parent / Guardian</div></div>
        <div class="panel-body">
          <form id="parent-add-form" class="stack">
            ${parentForm("parent")}
            <button type="submit">Add Parent</button>
          </form>
        </div>
      </aside>
    </div>
  `;

  const studentInput = document.querySelector("#parents-id");
  const list = document.querySelector("#parents-list");
  let loadedId = "";

  async function loadParents() {
    try {
      const payload = await api(`/api/students/${encodeURIComponent(studentInput.value.trim())}`);
      const student = payload.student;
      loadedId = student.student_id;
      list.innerHTML = `
        <div class="panel-header">
          <div class="panel-title">${escapeHtml(student.name)}</div>
          <span class="pill">${student.parents.length} contact(s)</span>
        </div>
        <div class="panel-body">${parentTable(student.parents, true)}</div>
      `;
      list.querySelectorAll(".parent-remove").forEach((button) => {
        button.addEventListener("click", async () => {
          try {
            await api(`/api/students/${encodeURIComponent(loadedId)}/parents/${button.dataset.index}`, {method: "DELETE"});
            showToast("Parent removed.");
            await loadParents();
          } catch (error) {
            showToast(error.message, "error");
          }
        });
      });
      setStatus(`Loaded parent contacts for ${student.name}.`);
    } catch (error) {
      showToast(error.message, "error");
    }
  }

  document.querySelector("#parents-load").addEventListener("click", loadParents);
  document.querySelector("#parent-add-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    if (!loadedId) {
      showToast("Load a student first.", "error");
      return;
    }
    try {
      await api(`/api/students/${encodeURIComponent(loadedId)}/parents`, {
        method: "POST",
        body: JSON.stringify(formData(form))
      });
      form.reset();
      document.querySelector("#parent-relationship").value = options.relationships[0] || "";
      showToast("Parent added.");
      await loadParents();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

function renderReports() {
  setActive("reports");
  setTitle("Reports");
  setStatus("Ready");
  app.innerHTML = `
    <div class="toolbar">
      <div class="field grow">
        <label for="report-id">Student ID</label>
        <input id="report-id">
      </div>
      <div class="field">
        <label for="report-type">Report</label>
        <select id="report-type">
          <option value="basic">Basic Student Report</option>
          <option value="detailed">Detailed Student Report</option>
        </select>
      </div>
      <button type="button" id="generate-report">Generate</button>
      <button type="button" class="secondary" id="risk-report">Attendance Risk</button>
      <button type="button" class="secondary" id="gpa-summary">GPA Summary</button>
    </div>
    <section class="panel" style="margin-top: 16px;">
      <div class="panel-header"><div class="panel-title">Report Output</div></div>
      <div class="panel-body">
        <textarea id="report-output" readonly></textarea>
      </div>
    </section>
  `;
  const output = document.querySelector("#report-output");

  document.querySelector("#generate-report").addEventListener("click", async () => {
    const studentId = document.querySelector("#report-id").value.trim();
    const type = document.querySelector("#report-type").value;
    try {
      const payload = await api(`/api/report?student_id=${encodeURIComponent(studentId)}&type=${encodeURIComponent(type)}`);
      output.value = payload.report;
      setStatus("Report generated.");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  document.querySelector("#risk-report").addEventListener("click", async () => {
    try {
      const payload = await api("/api/reports/attendance-risk");
      if (!payload.students.length) {
        output.value = "No students are currently below the attendance target.";
      } else {
        output.value = [
          "Students at Attendance Risk",
          "",
          ...payload.students.map((student) => `${student.student_id} - ${student.name}: ${student.attendance_percentage.toFixed(2)}%`)
        ].join("\n");
      }
      setStatus("Attendance risk report generated.");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  document.querySelector("#gpa-summary").addEventListener("click", async () => {
    try {
      const payload = await api("/api/reports/gpa-summary");
      const values = Object.entries(payload.gpa_map).sort(([first], [second]) => first.localeCompare(second));
      output.value = [
        "GPA Summary",
        "",
        `Class GPA average: ${payload.average_class_gpa.toFixed(2)}`,
        "",
        "Student GPA values:",
        ...(values.length ? values.map(([studentId, gpa]) => `${studentId}: ${Number(gpa).toFixed(2)}`) : ["No students found."])
      ].join("\n");
      setStatus("GPA summary generated.");
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

function renderStorage() {
  setActive("storage");
  setTitle("Save / Export Data");
  setStatus("Ready");
  app.innerHTML = `
    <div class="stack">
      <section class="panel">
        <div class="panel-header"><div class="panel-title">JSON Data</div></div>
        <div class="panel-body">
          <form id="json-form" class="stack">
            <div class="field">
              <label for="json-path">Path</label>
              <input id="json-path" name="path">
            </div>
            <div class="form-actions">
              <button type="button" id="save-json">Save JSON</button>
              <button type="button" class="secondary" id="load-json">Load JSON</button>
            </div>
          </form>
        </div>
      </section>
      <section class="panel">
        <div class="panel-header"><div class="panel-title">CSV Export</div></div>
        <div class="panel-body">
          <form id="csv-form" class="stack">
            <div class="field">
              <label for="csv-path">Path</label>
              <input id="csv-path" name="path">
            </div>
            <div class="form-actions">
              <button type="button" id="export-csv">Export CSV</button>
            </div>
          </form>
        </div>
      </section>
    </div>
  `;

  async function loadPaths() {
    const payload = await api("/api/options");
    document.querySelector("#json-path").value = payload.data_path;
    document.querySelector("#csv-path").value = payload.export_path;
  }

  async function storageAction(path, method, success) {
    try {
      const payload = {path: document.querySelector(path).value.trim()};
      await api(`/api/storage/${method}`, {method: "POST", body: JSON.stringify(payload)});
      showToast(success);
      setStatus(success);
      return true;
    } catch (error) {
      showToast(error.message, "error");
      return false;
    }
  }

  document.querySelector("#save-json").addEventListener("click", () => storageAction("#json-path", "save", "Data saved."));
  document.querySelector("#load-json").addEventListener("click", async () => {
    if (await storageAction("#json-path", "load", "Data loaded.")) {
      renderStudents();
    }
  });
  document.querySelector("#export-csv").addEventListener("click", () => storageAction("#csv-path", "export", "CSV exported."));
  loadPaths().catch((error) => showToast(error.message, "error"));
}

document.querySelectorAll(".nav-button").forEach((button) => {
  button.addEventListener("click", () => screens[button.dataset.screen]());
});

async function init() {
  try {
    options = await api("/api/options");
    await renderStudents();
  } catch (error) {
    showToast(error.message, "error");
    setStatus(error.message);
  }
}

init();
"""


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """HTTP server with thread-per-request handling."""

    daemon_threads = True
    allow_reuse_address = True


def parent_to_dict(parent: Parent) -> dict[str, str]:
    """Convert a parent object to JSON-friendly data."""
    return {
        "name": parent.name,
        "relationship": parent.relationship,
        "email": parent.email,
        "phone": parent.phone,
    }


def student_to_dict(student: Student) -> dict[str, Any]:
    """Convert a student object to JSON-friendly data for the web UI."""
    return {
        "student_id": student.student_id,
        "name": student.name,
        "age": student.age,
        "email": student.email,
        "phone": student.phone,
        "major": student.major,
        "year_level": student.year_level,
        "status": student.status,
        "grades": student.grades,
        "attendance": [
            {
                "date": record["date"],
                "present": record["present"],
                "label": attendance_label(record),
            }
            for record in student.attendance
        ],
        "parents": [parent_to_dict(parent) for parent in student.parents],
        "average_grade": student.average_grade(),
        "gpa": student.gpa(),
        "attendance_percentage": student.attendance_percentage(),
        "category": student.student_category(),
    }


def error_message(error: BaseException) -> str:
    """Return a clean message for HTTP error payloads."""
    if error.args:
        return str(error.args[0])
    return str(error)


def create_handler(
    manager: StudentManager,
    data_path: str,
    export_path: str = DEFAULT_EXPORT_PATH,
) -> type[http.server.BaseHTTPRequestHandler]:
    """Create a request handler bound to a manager instance."""

    class StudentWebHandler(http.server.BaseHTTPRequestHandler):
        server_version = "StudentDatabaseWeb/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            try:
                self._handle_get()
            except (KeyError, ValueError, RuntimeError, OSError) as error:
                self._send_json({"ok": False, "error": error_message(error)}, HTTPStatus.BAD_REQUEST)

        def do_POST(self) -> None:
            try:
                self._handle_post()
            except (KeyError, ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
                self._send_json({"ok": False, "error": error_message(error)}, HTTPStatus.BAD_REQUEST)

        def do_PATCH(self) -> None:
            try:
                self._handle_patch()
            except (KeyError, ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
                self._send_json({"ok": False, "error": error_message(error)}, HTTPStatus.BAD_REQUEST)

        def do_DELETE(self) -> None:
            try:
                self._handle_delete()
            except (KeyError, ValueError, RuntimeError, OSError) as error:
                self._send_json({"ok": False, "error": error_message(error)}, HTTPStatus.BAD_REQUEST)

        def _handle_get(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)

            if path in {"/", "/index.html"}:
                self._send_text(APP_HTML, "text/html; charset=utf-8")
                return
            if path == "/app.css":
                self._send_text(APP_CSS, "text/css; charset=utf-8")
                return
            if path == "/app.js":
                self._send_text(APP_JS, "application/javascript; charset=utf-8")
                return
            if path == "/api/options":
                self._send_json(
                    {
                        "ok": True,
                        "statuses": list(ALLOWED_STATUSES),
                        "year_levels": list(YEAR_LEVELS),
                        "relationships": list(ALLOWED_PARENT_RELATIONSHIPS),
                        "data_path": self.server.data_path,
                        "export_path": self.server.export_path,
                    }
                )
                return
            if path == "/api/students":
                self._send_json(self._students_payload(query))
                return
            if path.startswith("/api/students/"):
                student_id = self._path_part(path, 2)
                student = manager.get_student(student_id)
                self._send_json(
                    {
                        "ok": True,
                        "student": student_to_dict(student),
                        "detail_text": self._student_detail_text(student),
                    }
                )
                return
            if path == "/api/report":
                student_id = self._query_value(query, "student_id")
                report_type = self._query_value(query, "type", "basic")
                student = manager.get_student(student_id)
                report = BasicReport() if report_type == "basic" else DetailedReport()
                self._send_json({"ok": True, "report": report.generate(student)})
                return
            if path == "/api/reports/attendance-risk":
                students = [student_to_dict(student) for student in manager.students_at_risk()]
                self._send_json({"ok": True, "students": students})
                return
            if path == "/api/reports/gpa-summary":
                self._send_json(
                    {
                        "ok": True,
                        "average_class_gpa": manager.average_class_gpa(),
                        "gpa_map": manager.student_gpa_map(),
                    }
                )
                return

            self._send_json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

        def _handle_post(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            payload = self._read_json()

            if path == "/api/students":
                student = Student(
                    student_id=payload.get("student_id", ""),
                    name=payload.get("name", ""),
                    age=payload.get("age", ""),
                    email=payload.get("email", ""),
                    phone=payload.get("phone", ""),
                    major=payload.get("major", ""),
                    year_level=payload.get("year_level", ""),
                    status=payload.get("status", "Active"),
                )
                for parent in payload.get("parents", []):
                    student.add_parent(
                        name=parent.get("name", ""),
                        relationship=parent.get("relationship", ""),
                        email=parent.get("email", ""),
                        phone=parent.get("phone", ""),
                    )
                manager.add_student(student)
                self._send_json({"ok": True, "student": student_to_dict(student)})
                return

            if path.startswith("/api/students/") and path.endswith("/grades"):
                student_id = self._path_part(path, 2)
                manager.add_grade(student_id, payload.get("grade", ""))
                self._send_json({"ok": True, "student": student_to_dict(manager.get_student(student_id))})
                return

            if path.startswith("/api/students/") and path.endswith("/attendance"):
                student_id = self._path_part(path, 2)
                manager.add_attendance(
                    student_id,
                    payload.get("present", False),
                    payload.get("date") or None,
                )
                self._send_json({"ok": True, "student": student_to_dict(manager.get_student(student_id))})
                return

            if path.startswith("/api/students/") and path.endswith("/parents"):
                student_id = self._path_part(path, 2)
                manager.add_parent(
                    student_id,
                    name=payload.get("name", ""),
                    relationship=payload.get("relationship", ""),
                    email=payload.get("email", ""),
                    phone=payload.get("phone", ""),
                )
                self._send_json({"ok": True, "student": student_to_dict(manager.get_student(student_id))})
                return

            if path == "/api/storage/save":
                target = str(payload.get("path") or DEFAULT_DATA_PATH)
                manager.save_json(target)
                manager.data_path = target
                self.server.data_path = target
                self._send_json({"ok": True, "path": target})
                return

            if path == "/api/storage/load":
                target = str(payload.get("path") or DEFAULT_DATA_PATH)
                count = manager.load_json(target)
                manager.data_path = target
                self.server.data_path = target
                self._send_json({"ok": True, "path": target, "count": count})
                return

            if path == "/api/storage/export":
                target = str(payload.get("path") or DEFAULT_EXPORT_PATH)
                manager.export_csv(target)
                self.server.export_path = target
                self._send_json({"ok": True, "path": target})
                return

            self._send_json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

        def _handle_patch(self) -> None:
            path = urlparse(self.path).path
            if not path.startswith("/api/students/"):
                self._send_json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)
                return

            student_id = self._path_part(path, 2)
            payload = self._read_json()
            fields = {
                key: payload.get(key, "")
                for key in ("name", "age", "email", "phone", "major", "year_level", "status")
            }
            student = manager.update_student(student_id, **fields)
            self._send_json({"ok": True, "student": student_to_dict(student)})

        def _handle_delete(self) -> None:
            path = urlparse(self.path).path
            if path.startswith("/api/students/") and "/parents/" in path:
                parts = path.strip("/").split("/")
                student_id = unquote(parts[2])
                index = int(parts[4])
                removed = manager.remove_parent(student_id, index)
                self._send_json({"ok": True, "removed": parent_to_dict(removed)})
                return
            if path.startswith("/api/students/"):
                student_id = self._path_part(path, 2)
                removed = manager.delete_student(student_id)
                self._send_json({"ok": True, "student": student_to_dict(removed)})
                return

            self._send_json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

        def _students_payload(self, query: dict[str, list[str]]) -> dict[str, Any]:
            search = self._query_value(query, "search", "").strip()
            filter_type = self._query_value(query, "filter_type", "all")
            filter_value = self._query_value(query, "filter_value", "")

            if search:
                students = manager.search(search)
            elif filter_type == "major":
                students = manager.filter_by_major(filter_value)
            elif filter_type == "year":
                students = manager.filter_by_year_level(int(filter_value))
            elif filter_type == "status":
                students = manager.filter_by_status(filter_value)
            else:
                students = manager.all_students()

            status_counts = {status: 0 for status in ALLOWED_STATUSES}
            for student in manager.all_students():
                status_counts[student.status] = status_counts.get(student.status, 0) + 1

            return {
                "ok": True,
                "students": [student_to_dict(student) for student in students],
                "count": len(manager),
                "average_class_gpa": manager.average_class_gpa(),
                "majors": sorted(manager.unique_majors()),
                "status_counts": status_counts,
                "data_path": self.server.data_path,
                "export_path": self.server.export_path,
            }

        def _student_detail_text(self, student: Student) -> str:
            report = DetailedReport().generate(student)
            parent_lines = [
                f"{index}. {parent.name} ({parent.relationship}) - {parent.email}, {parent.phone}"
                for index, parent in enumerate(student.parents, start=1)
            ]
            parents = "\n".join(parent_lines) or "No parents recorded"
            return f"{report}\n\nParent Contacts:\n{parents}"

        def _query_value(
            self,
            query: dict[str, list[str]],
            key: str,
            default: str = "",
        ) -> str:
            values = query.get(key)
            if not values:
                return default
            return values[0]

        def _path_part(self, path: str, index: int) -> str:
            parts = path.strip("/").split("/")
            try:
                return unquote(parts[index])
            except IndexError as exc:
                raise ValueError("Invalid request path.") from exc

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length == 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)

        def _send_text(self, text: str, content_type: str) -> None:
            body = text.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(
            self,
            payload: dict[str, Any],
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return StudentWebHandler


def run_web_app(
    data_path: str = DEFAULT_DATA_PATH,
    host: str = "127.0.0.1",
    port: int = 8000,
    open_browser: bool = False,
) -> None:
    """Run the browser interface until interrupted."""
    manager = StudentManager(data_path=data_path)
    try:
        loaded_count = manager.load_json(data_path)
        startup_message = f"Loaded {loaded_count} student(s) from {data_path}."
    except (OSError, ValueError) as error:
        startup_message = f"Starting with an empty database: {error}"

    handler = create_handler(manager, data_path=data_path)
    server: ThreadingHTTPServer | None = None
    selected_port = port
    for candidate_port in range(port, port + 50):
        try:
            server = ThreadingHTTPServer((host, candidate_port), handler)
        except OSError:
            continue
        selected_port = candidate_port
        break

    if server is None:
        raise OSError(f"Could not bind a local web server on ports {port}-{port + 49}.")

    server.data_path = data_path
    server.export_path = DEFAULT_EXPORT_PATH
    url = f"http://{host}:{selected_port}"
    print(startup_message)
    print(f"Student Database interface running at {url}")
    print("Press Ctrl+C to stop the server.")
    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Student Database interface.")
    finally:
        server.server_close()
