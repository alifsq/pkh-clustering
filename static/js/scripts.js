// Modal for manual data entry
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal() {
    document.getElementById('manualDataModal').classList.add('hidden');
    document.getElementById('editModal').classList.add('hidden');
    document.getElementById('csvModal').classList.add('hidden');
}

function openEditModal(id, nik, nama, k_rumah, pekerjaan, gaji) {
    document.getElementById('editForm').action = `/editdata/${id}`;
    document.getElementById('edit_nik').value = nik;
    document.getElementById('edit_nama').value = nama;
    document.getElementById('edit_k_rumah').value = k_rumah;
    document.getElementById('edit_pekerjaan').value = pekerjaan;
    document.getElementById('edit_gaji').value = gaji;
    openModal('editModal');
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const header = document.getElementById('header');
    if (sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.remove('-translate-x-full');
        mainContent.classList.remove('ml-0');
        mainContent.classList.add('ml-64');
        header.classList.add('translate-x-64');
        // localStorage.setItem('sidebarState', 'open');
    } else {
        sidebar.classList.add('-translate-x-full');
        mainContent.classList.remove('ml-64');
        mainContent.classList.add('ml-0');
        header.classList.remove('translate-x-64');
        // localStorage.setItem('sidebarState', 'closed');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const sidebarState = localStorage.getItem('sidebarState');
    if (sidebarState === 'open') {
        toggleSidebar();
    }
});


