##
from flask import Flask, jsonify, request

# 假设我们有一个模拟的天气数据字典
weather_data = {
    'London': {'temperature': '16°C', 'description': 'Cloudy'},
    'New York': {'temperature': '22°C', 'description': 'Sunny'},
    'Tokyo': {'temperature': '26°C', 'description': 'Rainy'}
}

app = Flask(__name__)


@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')

    if city:
        city = city.capitalize()
        if city in weather_data:
            return jsonify(weather_data[city])
        else:
            return jsonify({'error': 'City not found'}), 404
    else:
        return jsonify({'error': 'City parameter is required'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=1999)

##
import sqlite3
import tkinter as tk
from tkinter import messagebox

# 创建客户管理系统的数据库连接
conn = sqlite3.connect('customer_management.db')
cursor = conn.cursor()

# 创建客户信息表格
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        UNIQUE(name, phone)
    )
''')
conn.commit()


# 定义客户管理系统的界面
class CustomerManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title('客户管理系统')

        # 创建界面元素
        self.label_name = tk.Label(root, text='姓名:')
        self.label_name.grid(row=0, column=0, padx=10, pady=5)
        self.entry_name = tk.Entry(root)
        self.entry_name.grid(row=0, column=1, padx=10, pady=5)

        self.label_phone = tk.Label(root, text='电话:')
        self.label_phone.grid(row=1, column=0, padx=10, pady=5)
        self.entry_phone = tk.Entry(root)
        self.entry_phone.grid(row=1, column=1, padx=10, pady=5)

        self.btn_add = tk.Button(root, text='添加客户', command=self.add_customer)
        self.btn_add.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='we')

        self.btn_show_all = tk.Button(root, text='显示所有客户', command=self.show_all_customers)
        self.btn_show_all.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='we')

        self.btn_search = tk.Button(root, text='搜索客户', command=self.search_customer)
        self.btn_search.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='we')

        self.btn_delete = tk.Button(root, text='删除客户', command=self.delete_customer)
        self.btn_delete.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='we')

        self.btn_quit = tk.Button(root, text='退出', command=self.on_quit)
        self.btn_quit.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky='we')

    def add_customer(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()

        if name == '':
            messagebox.showerror('错误', '姓名不能为空！')
            return

        cursor.execute('INSERT INTO customers (name, phone) VALUES (?, ?)', (name, phone))
        conn.commit()
        messagebox.showinfo('成功', f'已添加客户：{name}')
        self.entry_name.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
    def show_all_customers(self):
        cursor.execute('SELECT * FROM customers')
        customers = cursor.fetchall()
        if not customers:
            messagebox.showinfo('提示', '暂无客户信息！')
        else:
            result = '客户列表：\n'
            for customer in customers:
                result += f'ID: {customer[0]}, 姓名: {customer[1]}, 电话: {customer[2]}\n'
            messagebox.showinfo('客户信息', result)

    def search_customer(self):
        name = self.entry_name.get().strip()
        if name == '':
            messagebox.showerror('错误', '请输入要搜索的客户姓名！')
            return

        cursor.execute('SELECT * FROM customers WHERE name LIKE ?', (f'%{name}%',))
        customers = cursor.fetchall()
        if not customers:
            messagebox.showinfo('提示', f'未找到姓名包含"{name}"的客户！')
        else:
            result = '搜索结果：\n'
            for customer in customers:
                result += f'ID: {customer[0]}, 姓名: {customer[1]}, 电话: {customer[2]}\n'
            messagebox.showinfo('搜索结果', result)

    def delete_customer(self):
        """
        删除指定ID的客户
        """
        name = self.entry_name.get().strip()
        cursor.execute('DELETE FROM customers WHERE name = ?', (name,))
        conn.commit()
        print(f"成功删除ID为 {name} 的客户")

    def on_quit(self):
        conn.close()  # 关闭数据库连接
        root.quit()


# 主程序入口
if __name__ == '__main__':
    root = tk.Tk()
    app = CustomerManagementApp(root)
    root.mainloop()

# 关闭数据库连接
conn.close()
##
from torch.utils.data import Dataset
import json


class AFQMC(Dataset):
    def __init__(self, data_file):
        self.data = self.load_data(data_file)

    def load_data(self, data_file):
        Data = {}
        with open(data_file, 'rt') as f:
            for idx, line in enumerate(f):
                sample = json.loads(line.strip())
                Data[idx] = sample
        return Data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


train_data = AFQMC('data/afqmc_public/train.json')
valid_data = AFQMC('data/afqmc_public/dev.json')

print(train_data[0])
