from flask import Flask, render_template, request, redirect, url_for, session
from models import db, configure_database, DataPenerima, TransformedData, HasilClustering, Hasilduacluster, Hasiltigacluster,User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 
import plotly.express as px
from flask import flash
import pandas as pd
import io
import random
from datetime import datetime
import numpy as np
from sklearn.metrics import silhouette_score, silhouette_samples, pairwise_distances
from sklearn.cluster import KMeans


app = Flask(__name__)
configure_database(app)

# Konfigurasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('inputdata'))
        # render_template("dashboard.html") # Mengarahkan ke dashboard
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    return render_template('login.html')

# Tambahkan pengaturan untuk menangani pesan ketika user belum login
@login_manager.unauthorized_handler
def unauthorized():
    flash('Tolong login terlebih dahulu', 'info')  # Pesan flash khusus
    return redirect(url_for('login'))  # Redirect ke halaman login jika tidak login

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Total data
    total_data = DataPenerima.query.count()
    total_transformed_data = TransformedData.query.count()

    # Hitung total anggota per cluster
    clusteringresult_dua = Hasilduacluster.query.all()
    cluster_membership = {}
    for result in clusteringresult_dua:
        # Penomoran cluster dimulai dari 1
        cluster = result.cluster 
        cluster_membership[cluster] = cluster_membership.get(cluster, 0) + 1

    # Data untuk Pie Chart
    cluster_stats = [{'cluster': k, 'total': v} for k, v in cluster_membership.items()]
    cluster_df = pd.DataFrame(cluster_stats)

    # Buat Pie Chart dengan Plotly
    fig = px.pie(cluster_df, values='total', names='cluster', title='Cluster Membership Distribution')
    pie_chart2 = fig.to_html(full_html=False)

    # Hitung total anggota per cluster
    clusteringresult_tiga = Hasiltigacluster.query.all()
    cluster_membership = {}
    for result in clusteringresult_tiga:
        # Penomoran cluster dimulai dari 1
        cluster = result.cluster 
        cluster_membership[cluster] = cluster_membership.get(cluster, 0) + 1

    # Data untuk Pie Chart
    cluster_stats = [{'cluster': k, 'total': v} for k, v in cluster_membership.items()]
    cluster_df = pd.DataFrame(cluster_stats)

    # Buat Pie Chart dengan Plotly
    fig = px.pie(cluster_df, values='total', names='cluster', title='Cluster Membership Distribution')
    pie_chart3 = fig.to_html(full_html=False)
    
    return render_template(
        'dashboard.html',
        total_data=total_data,
        total_transformed_data=total_transformed_data,
        pie_chart2=pie_chart2,
        pie_chart3=pie_chart3
    )

@app.route('/inputdata', methods=['GET', 'POST'])
@login_required
def inputdata():
    if request.method == 'POST':
        tanggal = request.form['tanggal']
        nik = request.form['nik']
        nama = request.form['nama']
        k_rumah = request.form['k_rumah']
        pekerjaan = request.form['pekerjaan']
        gaji = request.form['gaji']
        
        new_data = DataPenerima(tanggal=tanggal, nik=nik, nama=nama, k_rumah=k_rumah, pekerjaan=pekerjaan, gaji=gaji)
        db.session.add(new_data)
        db.session.commit()
        
        return redirect(url_for('inputdata'))
    
    data_penerima = DataPenerima.query.all()
    return render_template('inputdata.html', data_penerima=data_penerima)

@app.route('/editdata/<int:id>', methods=['GET', 'POST'])
@login_required
def editdata(id):
    data = DataPenerima.query.get_or_404(id)
    if request.method == 'POST':
        tanggal = request.form['tanggal']
        data.nik = request.form['nik']
        data.nama = request.form['nama']
        data.k_rumah = request.form['k_rumah']
        data.pekerjaan = request.form['pekerjaan']
        data.gaji = request.form['gaji']
        
        db.session.commit()
        return redirect(url_for('inputdata'))
    
    return render_template('inputdata.html', edit_data=data)

@app.route('/deletedata/<int:id>')
@login_required
def deletedata(id):
    data = DataPenerima.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('inputdata'))

@app.route('/deletealldata')
@login_required
def deletealldata():
    try:
        db.session.query(TransformedData).delete()
        db.session.query(DataPenerima).delete()
        db.session.commit()
        return redirect(url_for('inputdata'))
    except Exception as e:
        db.session.rollback()
        return str(e)

@app.route('/uploadcsv', methods=['POST'])
@login_required
def uploadcsv():
    if 'csv_file' not in request.files:
        return "No file part"
    
    file = request.files['csv_file']
    
    if file.filename == '':
        return "No selected file"

    # Baca CSV dengan pandas
    try:
        data = pd.read_csv(file, dtype={'nik': str})

        # Bersihkan data
        data = data.dropna(subset=['tanggal','nik','nama', 'kondisi rumah', 'pekerjaan', 'gaji'])

        # Loop dan masukkan ke database
        for index, row in data.iterrows():
            if pd.isna(row['tanggal']) or pd.isna(row['nik']) or pd.isna(row['nama']) or pd.isna(row['kondisi rumah']) or pd.isna(row['pekerjaan']) or pd.isna(row['gaji']):
                continue
            new_item = DataPenerima(
                tanggal=row['tanggal'],
                nik=row['nik'],
                nama=row['nama'], 
                k_rumah=row['kondisi rumah'], 
                pekerjaan=row['pekerjaan'], 
                gaji=row['gaji']
            )
            db.session.add(new_item)
        db.session.commit()
        print(data.head())
    except Exception as e:
        return str(e)
    return redirect(url_for('inputdata'))

@app.route('/transformdata', methods=['POST'])
@login_required
def transformdata():
    data_penerima = DataPenerima.query.all()
    for data in data_penerima:
        transformed_k_rumah = transform_k_rumah(data.k_rumah)
        transformed_gaji = transform_gaji(data.gaji)
        transformed_pekerjaan = transform_pekerjaan(data.pekerjaan)
        
        existing_transformed_data = TransformedData.query.filter_by(id_penerima=data.id_penerima).first()
        if existing_transformed_data:
            existing_transformed_data.transformed_k_rumah = transformed_k_rumah
            existing_transformed_data.transformed_gaji = transformed_gaji
            existing_transformed_data.transformed_pekerjaan = transformed_pekerjaan
        else:
            transformed_data = TransformedData(
                id_penerima=data.id_penerima,
                transformed_k_rumah=transformed_k_rumah,
                transformed_gaji=transformed_gaji,
                transformed_pekerjaan=transformed_pekerjaan
            )
            db.session.add(transformed_data)
    db.session.commit()
    return redirect(url_for('inputdata'))

def transform_k_rumah(k_rumah):
    mapping = {'Baik': 0, 'Cukup': 1, 'Kurang': 2}
    return mapping.get(k_rumah, 0)

def transform_gaji(gaji):
    try:
        gaji = int(gaji)
    except (ValueError, TypeError):
        return 0
    if 0 <= gaji < 1500000:
        return 1
    elif 1500000 <= gaji <= 2000000:
        return 2
    elif 2000000 <= gaji <= 2500000:
        return 3
    elif 2500000 <= gaji <= 3000000:
        return 4
    elif gaji >= 3000000:
        return 4
    else:
        return None

def transform_pekerjaan(pekerjaan):
    mapping = {'Petani': 1, 'Wiraswasta': 2, 'Pedagang': 3, 'Serabutan': 4}
    return mapping.get(pekerjaan, 0)

@app.route('/praproses')
@login_required
def praproses():
    transformed_data = TransformedData.query.all()
    return render_template('praproses.html', transformed_data=transformed_data)


# num_clusters = 3  # Default number of clusters
# @app.route('/centroidawal', methods=['GET', 'POST'])
# def centroidawal():
#     global num_clusters
#     if request.method == 'POST':
#         num_clusters = int(request.form.get('num_clusters', 3))  # Default to 3 clusters if not specified
#         transformed_data = TransformedData.query.all()
#         data_points = [(data.transformed_k_rumah, data.transformed_gaji, data.transformed_pekerjaan) for data in transformed_data]
        
#         # Check if the number of clusters has changed or if initial_centroids are not in session
#         if 'initial_centroids' not in session or len(session['initial_centroids']) != num_clusters:
#             initial_centroids = random.sample(data_points, num_clusters)
#             session['initial_centroids'] = initial_centroids
#         else:
#             initial_centroids = session['initial_centroids']
        
#         return render_template('clustering.html', initial_centroids=initial_centroids, enumerate=enumerate)
    
#     return render_template('clustering.html')


@app.route('/2cluster')
@login_required
def duacluster():
    # Ambil data dari database
    transformed_data = TransformedData.query.all()
    
    if not transformed_data:
        return "No data available", 400  # Tangani jika tidak ada data
    
    # Konversi data ke numpy array untuk clustering
    data_points = np.array([
        (data.transformed_k_rumah, data.transformed_gaji, data.transformed_pekerjaan)
        for data in transformed_data
    ])
    
    # Jalankan algoritma K-Means dengan 2 cluster
    num_clusters = 2
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(data_points)
    labels = kmeans.labels_  # Hasil cluster untuk tiap data
    
    # Hapus data sebelumnya di tabel Hasilduacluster
    db.session.query(Hasilduacluster).delete()
    
    # Simpan hasil clustering ke tabel Hasilduacluster
    for data, cluster in zip(transformed_data, labels):
        hasil_duacluster = Hasilduacluster(
            id_penerima=data.id_penerima,  # Ambil id_penerima dari relasi
            cluster=int(cluster) + 1  # Cluster ID dimulai dari 1
        )
        db.session.add(hasil_duacluster)
    db.session.commit()
    
    # Hitung statistik untuk setiap cluster
    cluster_statsdua = []
    for cluster_id in range(num_clusters):
        cluster_data = data_points[labels == cluster_id]  # Ambil data sesuai label cluster
        cluster_statsdua.append({
            'cluster_id': cluster_id + 1,  # Cluster ID dimulai dari 1
            'min': cluster_data.min(axis=0).tolist() if len(cluster_data) > 0 else [None, None, None],
            'max': cluster_data.max(axis=0).tolist() if len(cluster_data) > 0 else [None, None, None],
            'mean': cluster_data.mean(axis=0).tolist() if len(cluster_data) > 0 else [None, None, None],
            'total': len(cluster_data)
        })

    # Hitung silhouette coefficient
    silhouette_avg = silhouette_score(data_points, labels)
    silhouette_values = silhouette_samples(data_points, labels)
    
    # Simpan hasil perhitungan ke session
    session['silhouette_avg'] = silhouette_avg
    session['silhouette_values'] = silhouette_values.tolist()
    session['cluster_assignments'] = labels.tolist()
    
    # Ambil data hasil clustering untuk ditampilkan
    hasil_duacluster = Hasilduacluster.query.all()
    
    # Kirim data dan hasil ke template
    return render_template(
        '2cluster.html',
        data=transformed_data,
        labels=labels,
        hasil_duacluster=hasil_duacluster,
        cluster_statsdua=cluster_statsdua,
        silhouette_avg=silhouette_avg,
        enumerate=enumerate
    )

@app.route('/3cluster')
@login_required
def tigacluster():
    # Ambil data dari database
    transformed_data = TransformedData.query.all()
    
    # Konversi data ke numpy array
    data_points = np.array([
        (data.transformed_k_rumah, data.transformed_gaji, data.transformed_pekerjaan)
        for data in transformed_data
    ])
    
    # Jalankan algoritma K-Means dengan 3 cluster
    kmeans = KMeans(n_clusters=3, random_state=0)
    kmeans.fit(data_points)
    labels = kmeans.labels_  # Hasil clustering
    
    # Hapus data hasil clustering sebelumnya
    db.session.query(Hasiltigacluster).delete()
    
    # Simpan hasil clustering ke database
    for data, cluster in zip(transformed_data, labels):
        hasil_tigacluster = Hasiltigacluster(
            id_penerima=data.id_penerima,  # Pastikan atribut ini ada
            cluster=int(cluster) + 1  # Cluster ID dimulai dari 1
        )
        db.session.add(hasil_tigacluster)
    db.session.commit()
    
     # Hitung statistik untuk setiap cluster
    cluster_statstiga = []
    for cluster_id in range(3):
        cluster_data = data_points[labels == cluster_id]  # Ambil data sesuai label cluster
        cluster_statstiga.append({
            'cluster_id': cluster_id + 1,  # Cluster ID dimulai dari 1
            'min': cluster_data.min(axis=0).tolist() if len(cluster_data) > 0 else [None, None, None],
            'max': cluster_data.max(axis=0).tolist() if len(cluster_data) > 0 else [None, None, None],
            'mean': cluster_data.mean(axis=0).tolist() if len(cluster_data) > 0 else [None, None, None],
            'total': len(cluster_data)
        })

    # Hitung silhouette coefficient
    silhouette_avg = silhouette_score(data_points, labels)
    silhouette_values = silhouette_samples(data_points, labels)
    
    # Simpan hasil perhitungan ke session
    session['silhouette_avg'] = silhouette_avg
    session['silhouette_values'] = silhouette_values.tolist()
    session['cluster_assignments'] = labels.tolist()
    
    # Ambil hasil clustering untuk ditampilkan
    hasil_tigacluster = Hasiltigacluster.query.all()
    
    # Kirim data ke template
    return render_template(
        '3cluster.html',
        data=transformed_data,
        labels=labels,
        hasil_tigacluster=hasil_tigacluster,
         cluster_statstiga=cluster_statstiga,
        silhouette_avg=silhouette_avg,
        enumerate=enumerate
    )

@app.route('/pengujian')
@login_required
def pengujian():
     # Ambil data dari database
    transformed_data = TransformedData.query.all()
    
    # Konversi data ke numpy array
    data_points = np.array([
        (data.transformed_k_rumah, data.transformed_gaji, data.transformed_pekerjaan)
        for data in transformed_data
    ])
    
    # Jalankan algoritma K-Means dengan 3 cluster
    kmeans = KMeans(n_clusters=3, random_state=0)
    kmeans.fit(data_points)
    labels = kmeans.labels_  # Hasil clustering
    
    if len(data_points) == 0 or len(labels) == 0:
        return "Clustering belum dilakukan. Silakan jalankan /3cluster terlebih dahulu.", 400

    # Hitung silhouette coefficient
    silhouette_avg = silhouette_score(data_points, labels)
    silhouette_values = silhouette_samples(data_points, labels)

    # Hitung a(i), b(i), dan s(i) untuk setiap data point
    results = []
    for i in range(len(data_points)):
        # a(i): Rata-rata jarak ke data point lain dalam cluster yang sama
        cluster = labels[i]
        mask = labels == cluster
        a_i = np.mean(np.linalg.norm(data_points[mask] - data_points[i], axis=1))

        # b(i): Rata-rata jarak ke data point dalam cluster terdekat
        b_i = np.inf
        for other_cluster in range(3):
            if other_cluster != cluster:
                mask_other = labels == other_cluster
                distance = np.mean(np.linalg.norm(data_points[mask_other] - data_points[i], axis=1))
                if distance < b_i:
                    b_i = distance

        # s(i): Nilai silhouette untuk data point ini
        s_i = silhouette_values[i]

        # Simpan hasil perhitungan
        results.append({
            'data_point': data_points[i].tolist(),
            'a_i': a_i,
            'b_i': b_i,
            's_i': s_i
        })

    # Kirim hasil ke template
    return render_template(
        'pengujian.html',
        silhouette_avg=silhouette_avg,
        results=results
    )

if __name__ == '__main__':
    app.run(debug=True)