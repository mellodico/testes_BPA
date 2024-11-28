import pandas as pd
import datetime
from pathlib import Path

class BPAGenerator:
    def __init__(self):
        self.HEADER_TYPE = "01"
        self.BPA_C_TYPE = "02"
        self.BPA_I_TYPE = "03"

    def generate_header(self, header_data: dict) -> str:
        """Gera linha de cabeçalho do arquivo BPA"""
        # Valores fixos apenas para simplificar
        total_lines = str(header_data.get('total_lines', 1)).zfill(6)
        total_sheets = str(header_data.get('total_sheets', 1)).zfill(6)
        control_field = "1111"
        
        # Formata campos do cabeçalho
        year_month = str(header_data['year_month']).ljust(6)
        org_name = str(header_data['org_name']).ljust(30)
        org_acronym = str(header_data['org_acronym']).ljust(6)
        cgc_cpf = str(header_data['cgc_cpf']).zfill(14)
        dest_name = str(header_data['dest_name']).ljust(40)
        dest_type = header_data['dest_type']
        version = str(header_data.get('version', '1.0.0')).ljust(10)
        
        # Gera linha
        header = (f"{self.HEADER_TYPE}#BPA#{year_month}{total_lines}{total_sheets}{control_field}"
                 f"{org_name}{org_acronym}{cgc_cpf}{dest_name}{dest_type}{version}\r\n")
        
        return header

    def generate_bpa_c(self, row: pd.Series) -> str:
        """Gera linha de BPA Consolidado"""
        line = self.BPA_C_TYPE
        line += str(row['cnes']).zfill(7)
        line += str(row['competencia']).zfill(6)
        line += str(row['cbo']).ljust(6)
        line += str(row['folha']).zfill(3)
        line += str(row['sequencial']).zfill(2)
        line += str(row['procedimento']).zfill(10)
        line += str(row['idade']).zfill(3)
        line += str(row['quantidade']).zfill(6)
        line += "EXT"  # Origem fixo
        line += "\r\n"
        
        return line

    def generate_bpa_i(self, row: pd.Series) -> str:
        """Gera linha de BPA Individualizado"""
        line = self.BPA_I_TYPE
        
        # Campos obrigatórios
        line += str(row['cnes']).zfill(7)
        line += str(row['competencia']).zfill(6)
        line += str(row['cns_profissional']).zfill(15)
        line += str(row['cbo']).ljust(6)
        
        # Converte data de string para data e depois para o formato correto
        data_atend = pd.to_datetime(row['data_atendimento']).strftime('%Y%m%d')
        line += data_atend
        
        line += str(row['folha']).zfill(3)
        line += str(row['sequencial']).zfill(2)
        line += str(row['procedimento']).zfill(10)
        line += str(row['cns_paciente']).zfill(15)
        line += str(row['sexo']).upper()
        line += str(row['codigo_municipio']).zfill(6)
        line += str(row['cid']).ljust(4)
        line += str(row['idade']).zfill(3)
        line += str(row['quantidade']).zfill(6)
        line += str(row.get('carater_atendimento', '01')).zfill(2)
        line += str(row.get('numero_autorizacao', '')).ljust(13)
        line += "EXT"  # Origem fixo
        line += str(row['nome_paciente']).ljust(30)
        
        # Converte data de nascimento
        dt_nasc = pd.to_datetime(row['data_nascimento']).strftime('%Y%m%d')
        line += dt_nasc
        
        line += str(row.get('raca', '01')).zfill(2)
        line += str(row.get('etnia', '')).ljust(4)
        line += str(row.get('nacionalidade', '010')).zfill(3)
        
        # Campos complementares com valores padrão
        service = str(row.get('servico', '')).ljust(3)
        classification = str(row.get('classificacao', '')).ljust(3)
        team_seq = str(row.get('equipe_seq', '')).ljust(8)
        team_area = str(row.get('equipe_area', '')).ljust(4)
        cnpj = str(row.get('cnpj', '')).ljust(14)
        cep = str(row.get('cep', '')).ljust(8)
        address_code = str(row.get('codigo_logradouro', '')).ljust(3)
        address = str(row.get('endereco', '')).ljust(30)
        complement = str(row.get('complemento', '')).ljust(10)
        number = str(row.get('numero', '')).ljust(5)
        neighborhood = str(row.get('bairro', '')).ljust(30)
        phone = str(row.get('telefone', '')).ljust(11)
        email = str(row.get('email', '')).ljust(40)
        ine = str(row.get('ine', '')).ljust(10)
        
        line += f"{service}{classification}{team_seq}{team_area}{cnpj}{cep}"
        line += f"{address_code}{address}{complement}{number}{neighborhood}"
        line += f"{phone}{email}{ine}\r\n"
        
        return line

def read_csv_file(filepath: str) -> pd.DataFrame:
    """Lê arquivo CSV e retorna DataFrame"""
    try:
        return pd.read_csv(filepath, dtype=str)
    except Exception as e:
        print(f"Erro ao ler arquivo {filepath}: {str(e)}")
        return None

def main():
    generator = BPAGenerator()
    
    # Solicita tipo de BPA
    print("Escolha o tipo de BPA:")
    print("1 - BPA Consolidado (BPA-C)")
    print("2 - BPA Individualizado (BPA-I)")
    bpa_type = input("Opção: ")
    
    # Solicita caminhos dos arquivos
    header_file = input("\nCaminho do arquivo CSV do cabeçalho: ")
    data_file = input("Caminho do arquivo CSV dos dados: ")
    
    # Lê arquivos CSV
    header_df = read_csv_file(header_file)
    data_df = read_csv_file(data_file)
    
    if header_df is None or data_df is None:
        print("Erro ao ler arquivos. Programa encerrado.")
        return
    
    # Pega primeira linha do cabeçalho
    header_data = header_df.iloc[0].to_dict()
    header_data['total_lines'] = len(data_df)
    header_data['total_sheets'] = len(data_df)  # Assume 1 registro por folha
    
    # Gera nome do arquivo de saída
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"BPA_{bpa_type}_{timestamp}.txt"
    
    # Gera arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        # Escreve cabeçalho
        f.write(generator.generate_header(header_data))
        
        # Escreve registros
        for _, row in data_df.iterrows():
            if bpa_type == "1":
                f.write(generator.generate_bpa_c(row))
            else:
                f.write(generator.generate_bpa_i(row))
    
    print(f"\nArquivo {output_file} gerado com sucesso!")

if __name__ == "__main__":
    main()