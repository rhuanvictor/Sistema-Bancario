import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                             QTextEdit)
from PyQt6.QtCore import Qt
from validators import format_cpf, is_valid_cpf
from styles import STYLE_SHEET

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Bancário - Login")
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.cpf_label = QLabel("CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setMaxLength(14)
        self.cpf_input.textChanged.connect(self.format_cpf_input)
        self.senha_label = QLabel("Senha:")
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Cadastrar-se")
        self.register_button.clicked.connect(self.register)

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)

        layout.addWidget(self.cpf_label)
        layout.addWidget(self.cpf_input)
        layout.addWidget(self.senha_label)
        layout.addWidget(self.senha_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.info_display)

        self.setLayout(layout)

    def format_cpf_input(self):
        text = self.cpf_input.text().replace('.', '').replace('-', '')
        if text.isdigit():
            formatted_cpf = format_cpf(text)
            self.cpf_input.setText(formatted_cpf)
            self.cpf_input.setCursorPosition(len(formatted_cpf))

    def login(self):
        cpf = self.cpf_input.text().replace('.', '').replace('-', '')
        senha = self.senha_input.text()

        if len(cpf) < 9:
            self.show_info("CPF inválido! O CPF deve ter pelo menos 9 dígitos.")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accounts WHERE cpf = ?", (cpf,))
        account = cursor.fetchone()

        if account:
            cursor.execute("SELECT * FROM accounts WHERE cpf = ? AND senha = ?", (cpf, senha))
            account = cursor.fetchone()
            if account:
                self.hide()
                self.bank_window = BankWindow(cpf)
                self.bank_window.show()
            else:
                self.show_info("Senha incorreta!")
        else:
            self.hide()
            self.registration_window = RegisterWindow(cpf, "CPF não encontrado. Precisa cadastrar.")
            self.registration_window.show()

        conn.close()

    def register(self):
        self.hide()
        self.registration_window = RegisterWindow()
        self.registration_window.show()

    def show_info(self, message):
        self.info_display.setText(message)

class RegisterWindow(QWidget):
    def __init__(self, cpf=None, info_message=None):
        super().__init__()
        self.setWindowTitle("Cadastro de Conta")
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui(cpf, info_message)

    def init_ui(self, cpf, info_message):
        layout = QVBoxLayout()

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        if info_message:
            self.info_display.setText(info_message)

        self.cpf_label = QLabel("CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setMaxLength(14)
        self.cpf_input.textChanged.connect(self.format_cpf_input)
        if cpf:
            self.cpf_input.setText(format_cpf(cpf))
            self.cpf_input.setEnabled(False)
        self.senha_label = QLabel("Senha:")
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton("Cadastrar")
        self.register_button.clicked.connect(self.register_account)

        self.back_button = QPushButton("Voltar")
        self.back_button.clicked.connect(self.go_back)

        layout.addWidget(self.info_display)
        layout.addWidget(self.cpf_label)
        layout.addWidget(self.cpf_input)
        layout.addWidget(self.senha_label)
        layout.addWidget(self.senha_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def format_cpf_input(self):
        text = self.cpf_input.text().replace('.', '').replace('-', '')
        if text.isdigit():
            formatted_cpf = format_cpf(text)
            self.cpf_input.setText(formatted_cpf)
            self.cpf_input.setCursorPosition(len(formatted_cpf))

    def register_account(self):
        cpf = self.cpf_input.text().replace('.', '').replace('-', '')
        senha = self.senha_input.text()

        if not is_valid_cpf(cpf):
            self.show_info("CPF inválido!")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO accounts (cpf, senha) VALUES (?, ?)", (cpf, senha))
            conn.commit()
            self.show_info("Conta cadastrada com sucesso!")
            self.hide()
            self.login_window = LoginWindow()
            self.login_window.show()
        except sqlite3.IntegrityError:
            self.show_info("CPF já cadastrado!")

        conn.close()

    def show_info(self, message):
        self.info_display.setText(message)

    def go_back(self):
        self.hide()
        self.login_window = LoginWindow()
        self.login_window.show()

class BankWindow(QWidget):
    def __init__(self, cpf):
        super().__init__()
        self.cpf = cpf
        self.setWindowTitle("Banco")
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)

        self.saldo_button = QPushButton("Consultar Saldo")
        self.saldo_button.clicked.connect(self.consultar_saldo)

        self.saque_label = QLabel("Valor do Saque:")
        self.saque_input = QLineEdit()
        self.saque_input.setPlaceholderText("0.00")
        self.saque_input.textChanged.connect(self.format_currency_input)

        self.saque_button = QPushButton("Sacar Dinheiro")
        self.saque_button.clicked.connect(self.sacar_dinheiro)

        self.deposito_label = QLabel("Valor do Depósito:")
        self.deposito_input = QLineEdit()
        self.deposito_input.setPlaceholderText("0.00")
        self.deposito_input.textChanged.connect(self.format_currency_input)

        self.deposito_button = QPushButton("Depositar Dinheiro")
        self.deposito_button.clicked.connect(self.depositar_dinheiro)

        self.extrato_button = QPushButton("Consultar Extrato")
        self.extrato_button.clicked.connect(self.consultar_extrato)

        self.sair_button = QPushButton("Sair")
        self.sair_button.clicked.connect(self.close_app)

        layout.addWidget(self.info_display)
        layout.addWidget(self.saldo_button)
        layout.addWidget(self.saque_label)
        layout.addWidget(self.saque_input)
        layout.addWidget(self.saque_button)
        layout.addWidget(self.deposito_label)
        layout.addWidget(self.deposito_input)
        layout.addWidget(self.deposito_button)
        layout.addWidget(self.extrato_button)
        layout.addWidget(self.sair_button)

        self.setLayout(layout)

    def format_currency_input(self):
        sender = self.sender()
        text = sender.text().replace('.', '').replace(',', '')
        if text.isdigit():
            try:
                # Converte o texto para float e divide por 100 para obter o valor em reais
                value = float(text) / 100
                # Formata o valor com 2 casas decimais, separador de milhares e ponto como separador decimal
                formatted_text = f"{value:,.2f}"
                sender.setText(formatted_text)
                sender.setCursorPosition(len(formatted_text))
               # print(f"Texto formatado: {formatted_text}")  # Exibe o valor formatado
            except ValueError:
                pass

    def consultar_saldo(self):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT saldo FROM accounts WHERE cpf = ?", (self.cpf,))
        saldo = cursor.fetchone()[0]

        print(f"Saldo armazenado no banco: {saldo:.2f}")  # Exibe o saldo armazenado

        self.show_info(f"Saldo atual: R${saldo:,.2f}")

        conn.close()

    def sacar_dinheiro(self):
        text = self.saque_input.text().replace('.', '').replace(',', '')
        valor = float(text) / 100 if text else 0
       # print(f"Valor digitado para saque: {valor:,.2f}")  # Exibe o valor digitado
        self.realizar_saque(valor)

    def realizar_saque(self, valor):
        if valor <= 0:
            self.show_info("O valor do saque deve ser maior que zero.")
            return

        if valor > 500:
            self.show_info("O valor do saque não pode ultrapassar R$500,00.")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT saldo, saques_diarios, ultimo_saque FROM accounts WHERE cpf = ?", (self.cpf,))
        resultado = cursor.fetchone()
        saldo = resultado[0]
        saques_diarios = resultado[1]
        ultimo_saque = resultado[2]

        hoje = datetime.now().strftime('%d-%m-%Y')

        if ultimo_saque == hoje:
            if saques_diarios >= 3:
                self.show_info("Você já realizou 3 saques hoje. Tente novamente amanhã.")
                conn.close()
                return
        else:
            saques_diarios = 0

        if valor > saldo:
            self.show_info("Saldo insuficiente para o saque.")
            conn.close()
            return

        novo_saldo = saldo - valor
        cursor.execute("UPDATE accounts SET saldo = ?, saques_diarios = ?, ultimo_saque = ? WHERE cpf = ?", 
                       (novo_saldo, saques_diarios + 1, hoje, self.cpf))
        cursor.execute("INSERT INTO transactions (cpf, tipo, valor, data) VALUES (?, 'Saque', ?, ?)",
                       (self.cpf, valor, hoje))

        conn.commit()
        self.show_info("Saque realizado com sucesso!")
        conn.close()

    def depositar_dinheiro(self):
        text = self.deposito_input.text().replace('.', '').replace(',', '')
        valor = float(text) / 100 if text else 0
        #print(f"Valor digitado para depósito: {valor:,.2f}")  # Exibe o valor digitado
        self.depositar(valor)

    def depositar(self, valor):
        if valor <= 0:
            self.show_info("O valor do depósito deve ser maior que zero.")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT saldo FROM accounts WHERE cpf = ?", (self.cpf,))
        saldo = cursor.fetchone()[0]

        novo_saldo = saldo + valor
        cursor.execute("UPDATE accounts SET saldo = ? WHERE cpf = ?", (novo_saldo, self.cpf))
        cursor.execute("INSERT INTO transactions (cpf, tipo, valor, data) VALUES (?, 'Depósito', ?, ?)",
                       (self.cpf, valor, datetime.now().strftime('%d-%m-%Y')))

        conn.commit()
        self.show_info("Depósito realizado com sucesso!")
        conn.close()

    def consultar_extrato(self):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT saldo FROM accounts WHERE cpf = ?", (self.cpf,))
        saldo = cursor.fetchone()[0]

        cursor.execute("SELECT tipo, valor, data FROM transactions WHERE cpf = ?", (self.cpf,))
        transacoes = cursor.fetchall()

        if transacoes:
            extrato = "Extrato de Transações:\n"
            for transacao in transacoes:
                # Corrigido o formato da data para '%d-%m-%Y' (com hífens)
                data_formatada = datetime.strptime(transacao[2], '%d-%m-%Y').strftime('%d/%m/%Y')
                extrato += f"{transacao[0]}: R${transacao[1]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + f" em {data_formatada}\n"
            extrato += f"\nSaldo atual: R${saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.show_info(extrato)
        else:
            self.show_info(f"Nenhuma transação encontrada.\n\nSaldo atual: R${saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

        conn.close()


    def show_info(self, text):
        self.info_display.setText(text)

    def close_app(self):
        self.close()
