from flask import Flask, request, redirect, render_template_string, send_file
import csv
import os
import io
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CSV_FILE = 'pedidos.csv'

# Dicionário de traduções
translations = {
    'pt': {
        'title': 'Painel de Pedidos',
        'id': 'ID',
        'name': 'Nome',
        'email': 'Email',
        'product': 'Produto',
        'payment_status': 'Status Pagamento',
        'shipping_status': 'Status Envio',
        'actions': 'Ações',
        'mark_paid': 'Marcar como pago',
        'save_tracking': 'Salvar Rastreio',
        'no_orders': 'Nenhum pedido encontrado.',
        'export_csv': 'Exportar CSV',
        'payment_pending': 'aguardando',
        'payment_done': 'pago',
        'shipping_done': 'enviado',
        'email_subject': 'Confirmação do pedido',
        'email_body': 'Olá {nome}, seu pedido {produto} está confirmado. Obrigado!',
    },
    'es': {
        'title': 'Panel de Pedidos',
        'id': 'ID',
        'name': 'Nombre',
        'email': 'Correo',
        'product': 'Producto',
        'payment_status': 'Estado de Pago',
        'shipping_status': 'Estado de Envío',
        'actions': 'Acciones',
        'mark_paid': 'Marcar como pagado',
        'save_tracking': 'Guardar Seguimiento',
        'no_orders': 'No se encontraron pedidos.',
        'export_csv': 'Exportar CSV',
        'payment_pending': 'pendiente',
        'payment_done': 'pagado',
        'shipping_done': 'enviado',
        'email_subject': 'Confirmación del pedido',
        'email_body': 'Hola {nome}, su pedido {produto} está confirmado. ¡Gracias!',
    },
    'en': {
        'title': 'Order Panel',
        'id': 'ID',
        'name': 'Name',
        'email': 'Email',
        'product': 'Product',
        'payment_status': 'Payment Status',
        'shipping_status': 'Shipping Status',
        'actions': 'Actions',
        'mark_paid': 'Mark as Paid',
        'save_tracking': 'Save Tracking',
        'no_orders': 'No orders found.',
        'export_csv': 'Export CSV',
        'payment_pending': 'pending',
        'payment_done': 'paid',
        'shipping_done': 'shipped',
        'email_subject': 'Order Confirmation',
        'email_body': 'Hello {nome}, your order {produto} is confirmed. Thank you!',
    },
    'de': {
        'title': 'Bestellübersicht',
        'id': 'ID',
        'name': 'Name',
        'email': 'Email',
        'product': 'Produkt',
        'payment_status': 'Zahlungsstatus',
        'shipping_status': 'Versandstatus',
        'actions': 'Aktionen',
        'mark_paid': 'Als bezahlt markieren',
        'save_tracking': 'Sendungsverfolgung speichern',
        'no_orders': 'Keine Bestellungen gefunden.',
        'export_csv': 'CSV exportieren',
        'payment_pending': 'wartend',
        'payment_done': 'bezahlt',
        'shipping_done': 'versandt',
        'email_subject': 'Bestellbestätigung',
        'email_body': 'Hallo {nome}, Ihre Bestellung {produto} wurde bestätigt. Danke!',
    },
}

def ler_pedidos():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def salvar_pedidos(lista):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=lista[0].keys())
        writer.writeheader()
        writer.writerows(lista)

def enviar_email(to_email, subject, body):
    # Exemplo simples usando SMTP local (ajustar conforme seu servidor)
    print(f"Enviando e-mail para {to_email} com assunto '{subject}'")
    # smtp = smtplib.SMTP('localhost')
    # msg = MIMEText(body)
    # msg['Subject'] = subject
    # msg['From'] = 'seu-email@dominio.com'
    # msg['To'] = to_email
    # smtp.send_message(msg)
    # smtp.quit()
    # Aqui só printa para simular envio
    print("E-mail enviado (simulado).")

@app.route('/')
def home():
    return redirect('/painel')

@app.route('/painel')
def painel():
    lang = request.args.get('lang', 'pt')
    if lang not in translations:
        lang = 'pt'
    t = translations[lang]

    pedidos = ler_pedidos()
    if not pedidos:
        return t['no_orders']

    html = f'<h1>{t["title"]}</h1>'
    html += f'<a href="/exportar-csv?lang={lang}">{t["export_csv"]}</a><br><br>'
    html += '<table border="1" cellpadding="5">'
    html += f'<tr><th>{t["id"]}</th><th>{t["name"]}</th><th>{t["email"]}</th><th>{t["product"]}</th><th>{t["payment_status"]}</th><th>{t["shipping_status"]}</th><th>{t["actions"]}</th></tr>'

    for p in pedidos:
        html += f"<tr><td>{p['id_pedido']}</td><td>{p['nome']}</td><td>{p['email']}</td><td>{p['produto']}</td>"
        html += f"<td>{p['status_pagamento']}</td><td>{p['status_envio']}</td><td>"
        if p['status_pagamento'] == t['payment_pending']:
            html += f"<a href='/marcar-pago/{p['id_pedido']}?lang={lang}'>{t['mark_paid']}</a><br>"
        if p['status_pagamento'] == t['payment_done'] and p['status_envio'] != t['shipping_done']:
            html += f"<form method='POST' action='/inserir-rastreio/{p['id_pedido']}?lang={lang}'><input name='codigo'><button type='submit'>{t['save_tracking']}</button></form>"
        html += "</td></tr>"

    html += '</table>'
    return render_template_string(html)

@app.route('/marcar-pago/<id>')
def marcar_pago(id):
    lang = request.args.get('lang', 'pt')
    if lang not in translations:
        lang = 'pt'

    pedidos = ler_pedidos()
    for p in pedidos:
        if p['id_pedido'] == id:
            p['status_pagamento'] = translations[lang]['payment_done']
            # Enviar email confirmando pagamento
            subject = translations[lang]['email_subject']
            body = translations[lang]['email_body'].format(nome=p['nome'], produto=p['produto'])
            enviar_email(p['email'], subject, body)
    salvar_pedidos(pedidos)
    return redirect(f'/painel?lang={lang}')

@app.route('/inserir-rastreio/<id>', methods=['POST'])
def inserir_rastreio(id):
    lang = request.args.get('lang', 'pt')
    if lang not in translations:
        lang = 'pt'
    codigo = request.form.get('codigo')
    pedidos = ler_pedidos()
    for p in pedidos:
        if p['id_pedido'] == id:
            p['codigo_rastreio'] = codigo
            p['status_envio'] = translations[lang]['shipping_done']
    salvar_pedidos(pedidos)
    return redirect(f'/painel?lang={lang}')

@app.route('/exportar-csv')
def exportar_csv():
    lang = request.args.get('lang', 'pt')
    if lang not in translations:
        lang = 'pt'

    if not os.path.exists(CSV_FILE):
        return translations[lang]['no_orders']

    return send_file(CSV_FILE, mimetype='text/csv', as_attachment=True, download_name='pedidos.csv')

if __name__ == '__main__':
    print(">> Servidor Flask iniciado")
    app.run(debug=True)
