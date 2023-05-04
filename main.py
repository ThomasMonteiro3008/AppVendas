from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
from functools import partial
from myfirebase import MyFireBase
from bannervendedor import BannerVendedor
from datetime import date

GUI = Builder.load_file("main.kv")
class MainApp(App):
    produto = None
    cliente = None
    unidade = None

    def build(self):
        self.firebase = MyFireBase()
        return GUI

    def on_start(self):

        arquivo = os.listdir('icones/fotos_perfil')
        pagina_fotoperfil = self.root.ids['fotoperfilpage']
        lista_fotos = pagina_fotoperfil.ids['lista_fotos_perfil']
        for foto in arquivo:
            imagem = ImageButton(source=f'icones/fotos_perfil/{foto}', on_release= partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)
        # carregar fotos dos clientes
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionar_vendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}",
                                 on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_cliente,foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)
        # carrear fotos dos produtos
        arquivos = os.listdir("icones/fotos_produtos")
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionar_vendas.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}",
                                 on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        #carregar a data
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        label_data = pagina_adicionar_vendas.ids["label_data"]
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        #carregar infos do usuario
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # pegar requisicao do usuario
            requisicao = requests.get(f'https://appvendas-283a2-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')
            requisicao_dic = requisicao.json()

            # preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'

            #preencher ID único

            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f"Seu ID Único: {id_vendedor}"

            # preencher total de vendas

            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            #preencher equipe

            self.equipe = requisicao_dic["equipe"]

            # preencher lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                         produto=venda['produto'], foto_produto=venda['foto_produto'],
                                         data=venda['data'], preco=venda['preco'],
                                         unidade=venda['unidade'], quantidade=venda['quantidade'])

                    lista_vendas.add_widget(banner)

            except Exception as mistake:
                print(mistake)
            # preencher equipe vendedores
                equipe = requisicao_dic["equipe"]
                lista_equipe = equipe.split(",")
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']

                for id_vendedor_equipe in lista_equipe:
                    if id_vendedor_equipe != "":
                        banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)

                        lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela("homepage")

        except Exception as mistake2:
            print(mistake2)

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'

        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f'https://appvendas-283a2-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                    data = info)

        self.mudar_tela('ajustespage')

    def adicionar_vendedor(self, id_vendedor_add):
        link = f'https://appvendas-283a2-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor_add"&equalTo="{id_vendedor_add}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        print(requisicao_dic)

        pagina_adicionar_vendedor = self.root.ids["adicionarvendedorpage"]
        mensagem = pagina_adicionar_vendedor.ids['mensagem_outrovendedor']

        if requisicao_dic == {}:
            mensagem.text = "Usuário não encontrado"

        else:
            equipe = self.equipe.split(",")
            if id_vendedor_add in equipe:
                mensagem.text = "Vendedor já faz parte da equipe"
            else:
                self.equipe = self.equipe + f",{id_vendedor_add}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f'https://appvendas-283a2-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',data=info)
                mensagem.text = "Vendedor adicionado com sucesso."
                #Adicionar um novo banner na equipe de vendedores
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_add)

                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):
        #deixar as letras na cor branca
        self.cliente = foto.replace('.png', '')
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionar_vendas.ids["lista_clientes"]

        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            #deixar as letras do item selecionado em azul
            try:
                texto = item.text
                texto = texto.lower()
                texto = texto + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        #deixar as letras na cor
        self.produto = foto.replace('.png', '')
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionar_vendas.ids["lista_produtos"]

        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            #deixar as letras do item selecionado em azul
            try:
                texto = item.text
                texto = texto.lower()
                texto = texto + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        #colorir todos de branco
        self.unidade = id_label.replace("unidades_", "")
        pagina_adicionar_vendas.ids["unidades_kg"].color  = (1, 1, 1, 1)
        pagina_adicionar_vendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionar_vendas.ids["unidades_litros"].color = (1, 1, 1, 1)

        #colorir o selecionado de azul
        pagina_adicionar_vendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionar_vendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionar_vendas.ids["preco_total"].text
        quantidade = pagina_adicionar_vendas.ids["quantidade_total"].text

        if not cliente:
            pagina_adicionar_vendas.ids["label_selecione_cliente"].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionar_vendas.ids["label_selecione_produto"].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionar_vendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionar_vendas.ids["unidades_unidades"].color = (1, 0, 0, 1)
            pagina_adicionar_vendas.ids["unidades_litros"].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionar_vendas.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionar_vendas.ids["label_preco"].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionar_vendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionar_vendas.ids["label_quantidade"].color = (1, 0, 0, 1)

        if produto and cliente and unidade and quantidade and preco and (type(preco) == float) and (type(quantidade) == float):
            foto_cliente = cliente + '.png'
            foto_produto = produto + '.png'

            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", ' \
                   f'"foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}" , ' \
                   f'"preco": "{preco}", "quantidade": "{quantidade}"}}'
            requests.post(f"https://appvendas-283a2-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}", data=info)

            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto,
                                 data=data, preco=preco, quantidade=quantidade, unidade=unidade)
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(banner)


            requisicao = requests.get(f"https://appvendas-283a2-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            total_vendas = float(requisicao.json())
            total_vendas += preco
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://appvendas-283a2-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)

            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            self.mudar_tela("homepage")

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_todasvendas = self.root.ids['todasvendaspage']
        lista_vendas = pagina_todasvendas.ids["lista_vendas"]
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # pegar requisicao da empresa
        requisicao = requests.get(f'https://appvendas-283a2-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()

        # preencher foto de perfil
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/hash.png'

        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                         produto=venda['produto'], foto_produto=venda['foto_produto'],
                                         data=venda['data'], preco=venda['preco'],
                                         unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except Exception as mistake:
                print(mistake)

        # preencher total de vendas


        pagina_todasvendas.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"


        self.mudar_tela("todasvendaspage")


    def sair_todasvendas(self, id_tela):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'

        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):

        try:
            vendas = dic_info_vendedor["vendas"]
            pagina_vendasoutrovendedor = self.root.ids['vendasoutrovendedorpage']
            lista_vendas = pagina_vendasoutrovendedor.ids['lista_vendas']

            #limpar todas as vendas
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)

            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                     produto=venda['produto'], foto_produto=venda['foto_produto'],
                                     data=venda['data'], preco=venda['preco'],
                                     unidade=venda['unidade'], quantidade=venda['quantidade'])
                lista_vendas.add_widget(banner)
        except Exception as mistake:
            print(mistake)

        # preencher total de vendas
        total_vendas = dic_info_vendedor["total_vendas"]
        pagina_vendasoutrovendedor.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

        # preencher foto de perfil
        foto_perfil = self.root.ids['foto_perfil']
        avatar = dic_info_vendedor["avatar"]
        foto_perfil.source = f'icones/fotos_perfil/{avatar}'

        self.mudar_tela('vendasoutrovendedorpage')

MainApp().run()
