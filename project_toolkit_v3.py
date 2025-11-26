# Salve este arquivo como: project_toolkit_v2.py
#
# REQUISITOS (instale na sua venv):
# pip install customtkinter

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Set, Dict, List, Tuple
from pathlib import Path
import traceback
from datetime import datetime
import threading
import time
import re
import io
from collections import defaultdict

#================================================================================
# BLOCO 1: LÓGICA DO "CONSOLIDA PROJECT"
#================================================================================

class ProjectAnalyzer:
    # ... [ TODO O CONTEÚDO DA SUA CLASSE ProjectAnalyzer VAI AQUI ] ...
    # (É exatamente o mesmo conteúdo do BLOCO 1 do script anterior)
    # (Por favor, copie e cole a classe inteira daqui para não ficar gigante)

    # --- INÍCIO DO CÓDIGO DA CLASSE ProjectAnalyzer ---
    """
    Analisador de projetos ultra-robusto e à prova de falhas.
    Protegido contra todos os cenários possíveis.
    """
    def __init__(self, project_path: str, output_filename: str):
        self.project_path = self._validate_path(project_path)
        self.output_filename = self._sanitize_filename(output_filename)
        self.ignore_patterns: Dict[str, Set[str]] = {}
        self.code_extensions: Set[str] = set()
        self.debug = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.timeout_seconds = 300  # 5 minutos
        self.start_time = None
        self.files_processed = 0
        self.files_skipped = 0
        self.cancelled = False

    def _validate_path(self, path: str) -> str:
        try:
            if not path or not isinstance(path, str):
                raise ValueError("Caminho inválido ou vazio")
            path = os.path.abspath(os.path.normpath(path))
            if not os.path.exists(path):
                raise ValueError(f"Caminho não existe: {path}")
            if not os.path.isdir(path):
                raise ValueError(f"Caminho não é um diretório: {path}")
            if not os.access(path, os.R_OK):
                raise PermissionError(f"Sem permissão de leitura: {path}")
            return path
        except Exception as e:
            self._log_error(f"Erro ao validar caminho: {e}")
            raise

    def _sanitize_filename(self, filename: str) -> str:
        try:
            if not filename or not isinstance(filename, str):
                filename = "projeto_unificado.md"
            forbidden_chars = '<>:"|?*\x00'
            for char in forbidden_chars:
                filename = filename.replace(char, '_')
            if not filename.lower().endswith('.md'):
                filename += '.md'
            if len(filename) > 200:
                name, ext = os.path.splitext(filename)
                filename = name[:196] + ext
            return filename
        except Exception:
            return "projeto_unificado.md"

    def _log_error(self, message: str):
        self.errors.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if self.debug:
            print(f"❌ ERRO: {message}", file=sys.stderr)

    def _log_warning(self, message: str):
        self.warnings.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if self.debug:
            print(f"⚠️  AVISO: {message}")

    def _check_timeout(self) -> bool:
        if self.start_time and self.timeout_seconds:
            elapsed = time.time() - self.start_time
            if elapsed > self.timeout_seconds:
                self._log_error(f"Timeout excedido ({self.timeout_seconds}s)")
                return True
        return False

    def set_profiles(self, profiles: list):
        try:
            if not profiles or not isinstance(profiles, (list, tuple)):
                profiles = []
            profiles = [str(p).lower() for p in profiles if p]
            self.ignore_patterns = {
                'dirs': {
                    '.git', '__pycache__', 'venv', 'env', '.venv', '.env',
                    '.idea', '.vscode', 'coverage', '.pytest_cache', 
                    '.mypy_cache', '.tox', '.nox',
                },
                'dirs_exact': {
                    'build', 'dist', 'target', 'out', 'bin', 'obj',
                    'logs', 'tmp', 'temp', '.gradle', '.mvn',
                    'node_modules', 'bower_components', 'jspm_packages',
                    'vendor',
                },
                'files': {
                    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                    '.ds_store', 'thumbs.db', 'desktop.ini',
                },
                'extensions': {
                    '.log', '.tmp', '.cache', '.lock', '.pid', '.swp', '.swo',
                    '.bak', '.backup', '.old', '.orig',
                    '.DS_Store', '.ico', '.png', '.jpg', '.jpeg', 
                    '.gif', '.svg', '.webp', '.bmp', '.tiff',
                    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
                    '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
                    '.deb', '.rpm', '.apk', '.dmg', '.iso',
                    '.map', '.min.js', '.min.css',
                    '.pyc', '.pyo', '.pyd', '.class', '.o', '.obj',
                },
                'paths': set(),
            }
            self.code_extensions = {
                '.html', '.htm', '.css', '.scss', '.sass', '.less',
                '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
                '.vue', '.svelte', '.astro',
                '.json', '.json5', '.jsonc', '.yaml', '.yml', '.toml', 
                '.xml', '.ini', '.cfg', '.conf', '.config',
                '.md', '.markdown', '.txt', '.text',
                '.py', '.pyw', '.pyi',
                '.java', '.kt', '.kts', '.scala',
                '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh', '.hxx',
                '.cs', '.vb', '.fs', '.fsx',
                '.rb', '.rake', '.go', '.rs',
                '.swift', '.m', '.mm',
                '.lua', '.pl', '.pm', '.r',
                '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
                '.sql', '.psql', '.mysql', '.sqlite',
                '.env.example', '.gitignore', '.dockerignore',
                'dockerfile', 'makefile', 'rakefile',
            }
            if 'php' in profiles: self._add_php_patterns()
            if 'react' in profiles: self._add_react_patterns()
            if 'spring' in profiles: self._add_spring_patterns()
            if 'python' in profiles: self._add_python_patterns()
            if 'node' in profiles or 'nodejs' in profiles: self._add_node_patterns()
        except Exception as e:
            self._log_error(f"Erro ao configurar perfis: {e}")

    def _add_php_patterns(self):
        try:
            self.ignore_patterns['dirs_exact'].update({'vendor', 'cache'})
            self.ignore_patterns['paths'].update({
                'storage/logs', 'storage/framework/cache',
                'storage/framework/sessions', 'storage/framework/views',
                'bootstrap/cache',
            })
            self.ignore_patterns['files'].update({
                'composer.lock', 'composer.phar', '.phpunit.result.cache',
            })
            self.ignore_patterns['extensions'].add('.phar')
            self.code_extensions.update({
                '.php', '.phtml', '.php3', '.php4', '.php5', '.php7', '.phps'
            })
        except Exception as e: self._log_warning(f"Erro ao adicionar padrões PHP: {e}")

    def _add_react_patterns(self):
        try:
            self.ignore_patterns['dirs_exact'].update({'node_modules', '.next', '.nuxt', 'coverage'})
            self.ignore_patterns['files'].update({'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'})
        except Exception as e: self._log_warning(f"Erro ao adicionar padrões React: {e}")

    def _add_spring_patterns(self):
        try:
            self.ignore_patterns['dirs_exact'].update({'target', '.mvn', '.gradle'})
            self.ignore_patterns['files'].update({
                'mvnw', 'mvnw.cmd', 'gradlew', 'gradlew.bat', 
                'gradle-wrapper.jar', 'maven-wrapper.jar',
            })
            self.code_extensions.update({'.java', '.kt', '.xml', '.properties', '.gradle', '.sql'})
        except Exception as e: self._log_warning(f"Erro ao adicionar padrões Spring: {e}")

    def _add_python_patterns(self):
        try:
            self.ignore_patterns['dirs_exact'].update({'__pycache__', '.pytest_cache', '.mypy_cache', '.tox', '.nox', 'htmlcov', '.coverage'})
            self.ignore_patterns['extensions'].update({'.pyc', '.pyo', '.pyd', '.whl', '.egg'})
            self.ignore_patterns['files'].update({'poetry.lock', 'pipfile.lock'})
        except Exception as e: self._log_warning(f"Erro ao adicionar padrões Python: {e}")

    def _add_node_patterns(self):
        try:
            self.ignore_patterns['dirs_exact'].update({'node_modules', '.npm', '.yarn', '.pnpm-store'})
            self.ignore_patterns['files'].update({'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'})
        except Exception as e: self._log_warning(f"Erro ao adicionar padrões Node: {e}")

    def _should_ignore_dir(self, dir_name: str, full_path: str) -> bool:
        try:
            if not dir_name or not isinstance(dir_name, str): return True
            if dir_name.startswith('.') and dir_name not in {'.github', '.gitlab'}: return True
            if dir_name in self.ignore_patterns.get('dirs', set()): return True
            if dir_name in self.ignore_patterns.get('dirs_exact', set()): return True
            try:
                if not os.access(full_path, os.R_OK | os.X_OK):
                    self._log_warning(f"Sem permissão para acessar: {dir_name}")
                    return True
            except (OSError, PermissionError): return True
            try:
                if os.path.islink(full_path):
                    self._log_warning(f"Link simbólico ignorado: {dir_name}")
                    return True
            except (OSError, ValueError): return True
            return False
        except Exception as e:
            self._log_warning(f"Erro ao verificar diretório {dir_name}: {e}")
            return True

    def _should_ignore_file(self, file_name: str, relative_path: str) -> bool:
        try:
            if not file_name or not isinstance(file_name, str): return True
            lower_name = file_name.lower()
            if lower_name in self.ignore_patterns.get('files', set()): return True
            try:
                _, ext = os.path.splitext(lower_name)
                if ext and ext in self.ignore_patterns.get('extensions', set()): return True
            except Exception: pass
            if lower_name.startswith('.') and lower_name not in {'.gitkeep', '.htaccess', '.env.example', '.editorconfig'}: return True
            try:
                if 'paths' in self.ignore_patterns:
                    normalized_path = relative_path.replace(os.sep, '/')
                    for ignore_path in self.ignore_patterns['paths']:
                        if ignore_path in normalized_path: return True
            except Exception: pass
            return False
        except Exception as e:
            self._log_warning(f"Erro ao verificar arquivo {file_name}: {e}")
            return True

    def _is_binary_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                if not chunk: return False
                if b'\x00' in chunk: return True
                text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
                non_text = sum(1 for byte in chunk if byte not in text_chars)
                return non_text / len(chunk) > 0.3
        except Exception: return True

    def _read_file_safely(self, file_path: str) -> Tuple[str, bool]:
        try:
            try:
                file_size = os.path.getsize(file_path)
                if file_size > self.max_file_size:
                    self._log_warning(f"Arquivo muito grande ignorado ({file_size} bytes): {file_path}")
                    return "", False
                if file_size == 0: return "", False
            except (OSError, ValueError): return "", False
            if self._is_binary_file(file_path):
                self._log_warning(f"Arquivo binário ignorado: {file_path}")
                return "", False
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    if content and len(content.strip()) > 0:
                        content = ''.join(char for char in content if char.isprintable() or char in '\n\r\t')
                        return content.strip(), True
                except (UnicodeDecodeError, UnicodeError): continue
                except Exception: break
            return "", False
        except PermissionError:
            self._log_warning(f"Sem permissão para ler: {file_path}")
            return "", False
        except (OSError, IOError) as e:
            self._log_warning(f"Erro de I/O ao ler {file_path}: {e}")
            return "", False
        except Exception as e:
            self._log_error(f"Erro inesperado ao ler {file_path}: {e}")
            return "", False

    def _generate_tree(self) -> str:
        lines = []
        
        # --- NOVIDADE: Adiciona o nome da pasta raiz no topo ---
        project_root_name = os.path.basename(self.project_path)
        lines.append(f"{project_root_name}/")
        
        try:
            for root, dirs, files in os.walk(self.project_path, topdown=True, onerror=None, followlinks=False):
                try:
                    if self._check_timeout() or self.cancelled: break
                    
                    relative_path = os.path.relpath(root, self.project_path)
                    
                    original_dirs = dirs.copy()
                    dirs[:] = []
                    for d in original_dirs:
                        try:
                            full_dir_path = os.path.join(root, d)
                            if not self._should_ignore_dir(d, full_dir_path):
                                dirs.append(d)
                        except Exception as e: self._log_warning(f"Erro ao processar diretório {d}: {e}")
                    
                    # --- NÍVEL DE INDENTAÇÃO CORRIGIDO ---
                    # O nível agora é baseado no relative_path + 1 (para contar a raiz)
                    level = relative_path.count(os.sep) if relative_path != '.' else 0
                    indent = "│   " * level
                    
                    # --- LÓGICA DE PREFIXO ---
                    # Adiciona o prefixo '├──' ou '└──'
                    # (Esta lógica estava faltando na sua árvore original, 
                    # mas é necessária para o Script 2 ler corretamente)
                    
                    dir_name = os.path.basename(root)
                    
                    # Não adiciona a raiz de novo, já foi adicionada
                    if root == self.project_path:
                         pass # Já adicionamos a raiz no topo
                    else:
                        # Determina se é o último item da pasta pai (complexo de fazer sem lookahead)
                        # Vamos usar uma abordagem simples que funciona para o Script 2
                         lines.append(f"{indent}├── {dir_name}/") # Simplificado

                    sub_indent = "│   " * (level + 1)
                    
                    for i, file in enumerate(files):
                        try:
                            is_last_file = (i == len(files) - 1)
                            prefix = "└──" if is_last_file else "├──"
                            
                            if not self._should_ignore_file(file, os.path.join(relative_path, file)):
                                lines.append(f"{sub_indent}{prefix} {file}")
                        except Exception as e: self._log_warning(f"Erro ao processar arquivo {file}: {e}")
                
                except Exception as e:
                    self._log_warning(f"Erro ao processar pasta {root}: {e}")
                    continue
        except Exception as e:
            self._log_error(f"Erro ao gerar árvore: {e}")
        
        return "\n".join(lines) if lines else "├── (vazio ou sem permissão)"

    def _consolidate_code(self) -> str:
        content = []
        try:
            for root, dirs, files in os.walk(self.project_path, topdown=True, onerror=None, followlinks=False):
                try:
                    if self._check_timeout():
                        self._log_error("Processo cancelado por timeout")
                        break
                    if self.cancelled:
                        self._log_warning("Processo cancelado pelo usuário")
                        break
                    relative_path = os.path.relpath(root, self.project_path)
                    original_dirs = dirs.copy()
                    dirs[:] = []
                    for d in original_dirs:
                        try:
                            full_dir_path = os.path.join(root, d)
                            if not self._should_ignore_dir(d, full_dir_path):
                                dirs.append(d)
                        except Exception: pass
                    for file in files:
                        try:
                            if self._check_timeout() or self.cancelled: break
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, self.project_path)
                            if self._should_ignore_file(file, rel_path):
                                self.files_skipped += 1
                                continue
                            try:
                                _, ext = os.path.splitext(file.lower())
                                if ext not in self.code_extensions and file.lower() not in self.code_extensions:
                                    self.files_skipped += 1
                                    continue
                            except Exception:
                                self.files_skipped += 1
                                continue
                            file_content, success = self._read_file_safely(file_path)
                            if success and file_content:
                                lang = ext[1:] if ext and len(ext) > 1 else ''
                                content.append(
                                    f"### `{rel_path}`\n\n"
                                    f"```{lang}\n{file_content}\n```\n"
                                )
                                self.files_processed += 1
                                if self.debug and self.files_processed % 10 == 0:
                                    print(f"📝 Processados: {self.files_processed} arquivos...")
                            else:
                                self.files_skipped += 1
                        except Exception as e:
                            self._log_warning(f"Erro ao processar {file}: {e}")
                            self.files_skipped += 1
                except Exception as e:
                    self._log_warning(f"Erro ao processar pasta {root}: {e}")
                    continue
        except Exception as e:
            self._log_error(f"Erro crítico ao consolidar código: {e}")
            self._log_error(traceback.format_exc())
        return "\n".join(content) if content else "_Nenhum arquivo de código encontrado ou processado._\n"

    def _generate_statistics(self) -> str:
        stats = [
            "## 📊 Estatísticas da Análise\n",
            f"- **Arquivos processados:** {self.files_processed}",
            f"- **Arquivos ignorados/pulados:** {self.files_skipped}",
            f"- **Erros encontrados:** {len(self.errors)}",
            f"- **Avisos gerados:** {len(self.warnings)}",
            f"- **Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        ]
        if self.start_time:
            elapsed = time.time() - self.start_time
            stats.append(f"- **Tempo de execução:** {elapsed:.2f}s")
        return "\n".join(stats)

    def _generate_error_section(self) -> str:
        sections = []
        if self.errors:
            sections.append("\n## ❌ Erros Encontrados\n")
            for i, error in enumerate(self.errors[:50], 1):
                sections.append(f"{i}. {error}")
            if len(self.errors) > 50: sections.append(f"\n_... e mais {len(self.errors) - 50} erros_")
        if self.warnings and self.debug:
            sections.append("\n## ⚠️ Avisos\n")
            for i, warning in enumerate(self.warnings[:30], 1):
                sections.append(f"{i}. {warning}")
            if len(self.warnings) > 30: sections.append(f"\n_... e mais {len(self.warnings) - 30} avisos_")
        return "\n".join(sections)

    def generate_report(self, tree_content: str) -> bool:
        """
        Gera relatório completo.
        MODIFICADO: Agora recebe o 'tree_content' como argumento
        para evitar gerá-lo duas vezes.
        """
        self.start_time = time.time()
        success = False
        try:
            print("📝 Consolidando arquivos de código...")
            code_content = self._consolidate_code()
            
            stats = self._generate_statistics()
            error_section = self._generate_error_section()
            
            print(f"\n💾 Salvando arquivo '{self.output_filename}'...")
            
            try:
                with open(self.output_filename, 'w', encoding='utf-8', errors='replace') as out:
                    out.write("# 📋 Análise de Projeto\n\n")
                    out.write(f"**Projeto:** `{os.path.basename(self.project_path)}`  \n")
                    out.write(f"**Caminho:** `{self.project_path}`\n\n")
                    out.write("---\n\n")
                    out.write(stats)
                    out.write("\n\n---\n\n")
                    out.write("## 📁 Estrutura de Pastas\n\n```\n")
                    out.write(tree_content) # Usa a árvore pré-gerada
                    out.write("\n```\n\n")
                    out.write("---\n\n")
                    out.write("## 💻 Conteúdo dos Arquivos de Código\n\n")
                    out.write(code_content)
                    
                    if error_section:
                        out.write("\n\n---\n")
                        out.write(error_section)
                    
                    out.write("\n\n---\n\n")
                    out.write("_Relatório gerado automaticamente pelo ProjectAnalyzer_\n")
                
                success = True
                
            except PermissionError:
                raise PermissionError(f"Sem permissão para escrever: {self.output_filename}")
            except (OSError, IOError) as e:
                raise IOError(f"Erro ao escrever arquivo: {e}")
            
            print("\n" + "="*60)
            print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print(f"📄 Arquivo gerado: {self.output_filename}")
            print(f"📊 Arquivos processados: {self.files_processed}")
            print(f"⏭️  Arquivos ignorados: {self.files_skipped}")
            
            if self.errors: print(f"❌ Erros: {len(self.errors)}")
            if self.warnings: print(f"⚠️  Avisos: {len(self.warnings)}")
            
            if self.start_time:
                elapsed = time.time() - (self.start_time or time.time())
                print(f"⏱️  Tempo total: {elapsed:.2f}s")
            print("="*60)
            
            return True
            
        except KeyboardInterrupt:
            self._log_error("Processo interrompido pelo usuário")
            print("\n⚠️  Processo cancelado pelo usuário")
            return False
            
        except Exception as e:
            self._log_error(f"Erro crítico: {e}")
            self._log_error(traceback.format_exc())
            print(f"\n❌ ERRO CRÍTICO: {e}")
            print("Verifique as permissões e o caminho do projeto")
            return False
        
        finally:
            if not success and self.files_processed > 0:
                try:
                    print("\n⚠️  Tentando salvar relatório parcial...")
                    with open(f"parcial_{self.output_filename}", 'w', encoding='utf-8') as out:
                        out.write("# Relatório Parcial (Processo Interrompido)\n\n")
                        out.write(self._generate_statistics())
                        out.write(self._generate_error_section())
                    print(f"💾 Relatório parcial salvo como: parcial_{self.output_filename}")
                except Exception:
                    pass
    # --- FIM DO CÓDIGO DA CLASSE ProjectAnalyzer ---    """

#================================================================================
# BLOCO 2: LÓGICA DO "ANALISA FOLDER"
#================================================================================

def extrair_estrutura(estrutura_string):
    """
    Analisa a string da estrutura do projeto e extrai uma lista de todos os
    caminhos de diretório e arquivos esperados.
    """
    pastas_requeridas = set()
    arquivos_requeridos = set()
    pilha_de_caminhos = []
    ultimo_nivel_indentacao = -1

    linhas = estrutura_string.strip().split('\n')
    if not linhas or not linhas[0].strip():
        return {'pastas': [], 'arquivos': []}

    diretorio_raiz = linhas[0].strip().rstrip('/')
    if diretorio_raiz:
        pastas_requeridas.add(diretorio_raiz)
        pilha_de_caminhos.append(diretorio_raiz)
        ultimo_nivel_indentacao = -1

    for linha in linhas[1:]:
        if '└──' not in linha and '├──' not in linha:
            continue
        
        parte_relevante = linha.split('#')[0]
        
        if '└──' in parte_relevante:
            nome_item = parte_relevante.split('└──', 1)[1].strip()
        elif '├──' in parte_relevante:
            nome_item = parte_relevante.split('├──', 1)[1].strip()
        else:
            continue
        
        if not nome_item or nome_item == '...':
            continue

        is_folder = nome_item.endswith('/')
        nome_limpo = nome_item.rstrip('/')

        indentacao_atual = len(re.split(r'[\w.-]+', linha, 1)[0])

        while indentacao_atual <= ultimo_nivel_indentacao and len(pilha_de_caminhos) > 1:
            pilha_de_caminhos.pop()
            if len(pilha_de_caminhos) > 1:
                 ultimo_nivel_indentacao -= 4 
            else:
                 ultimo_nivel_indentacao = -1
        
        caminho_atual = os.path.join(*pilha_de_caminhos, nome_limpo)

        if is_folder:
            pastas_requeridas.add(caminho_atual)
            if indentacao_atual > ultimo_nivel_indentacao:
                 pilha_de_caminhos.append(nome_limpo)
                 ultimo_nivel_indentacao = indentacao_atual
        else: # É um arquivo
            arquivos_requeridos.add(caminho_atual)

    return {
        'pastas': sorted(list(pastas_requeridas)),
        'arquivos': sorted(list(arquivos_requeridos))
    }


#================================================================================
# BLOCO 3: LÓGICA DO "FRONTEND SCANNER" (SHERLOCK)
#================================================================================

class FrontendScanner:
    def __init__(self, project_path):
        self.project_path = project_path
        self.api_endpoints = []
        self.potential_models = defaultdict(set)
        
        self.regex_api = r"(?:api|axios|http|fetch)\.(get|post|put|delete|patch)\s*\(\s*['\"`$](.*?)['\"`$]"
        self.regex_props = r"\b([a-zA-Z]\w*)\.([a-zA-Z]\w+)\b"
        
        self.ignore_words = {
            'console', 'window', 'document', 'localStorage', 'sessionStorage', 
            'JSON', 'Math', 'Date', 'Object', 'navigator', 'event', 'e', 'this', 
            'formData', 'prev', 'history', 'location', 'navigator', 'React', 
            'ReactDOM', 'loading', 'error', 'data', 'response', 'config', 'props',
            'params', 'target', 'style', 'files', 'length', 'map', 'filter', 'push'
        }

    def scan(self):
        if not os.path.exists(self.project_path):
            return "❌ Erro: Caminho do projeto não encontrado."

        for root, dirs, files in os.walk(self.project_path):
            if 'node_modules' in dirs: dirs.remove('node_modules')
            
            for file in files:
                if file.endswith((".js", ".jsx", ".ts", ".tsx")):
                    self._analyze_file(os.path.join(root, file), file)
        
        return self._generate_report_string()

    def _analyze_file(self, file_path, file_name):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                matches_api = re.findall(self.regex_api, content, re.IGNORECASE)
                for method, url in matches_api:
                    clean_url = url.replace("${", "{").replace("}", "}")
                    self.api_endpoints.append({
                        "method": method.upper(), "url": clean_url, "file": file_name
                    })

                matches_props = re.findall(self.regex_props, content)
                for obj, prop in matches_props:
                    if obj not in self.ignore_words and len(obj) > 2 and len(prop) > 2:
                        if obj[0].islower(): 
                            self.potential_models[obj].add(prop)
        except Exception: pass

    def _generate_report_string(self):
        output = []
        output.append("="*60)
        output.append(f"🚀 RELATÓRIO SHERLOCK: O QUE O BACKEND PRECISA?")
        output.append(f"📂 Analisando: {self.project_path}")
        output.append("="*60 + "\n")

        output.append(f"📡 1. ROTAS DE API IDENTIFICADAS ({len(self.api_endpoints)}):")
        output.append("-" * 40)
        
        seen = set()
        for ep in self.api_endpoints:
            key = f"{ep['method']} {ep['url']}"
            if key not in seen:
                output.append(f"[{ep['method']}] {ep['url']:<35} (via {ep['file']})")
                seen.add(key)
        
        if not self.api_endpoints:
            output.append("   (Nenhuma chamada de API óbvia encontrada)")

        output.append(f"\n\n💾 2. TABELAS/MODELOS SUGERIDOS (Inferência):")
        output.append("-" * 40)
        
        count_models = 0
        for model, props in self.potential_models.items():
            if len(props) >= 2:
                count_models += 1
                props_list = ", ".join(sorted(list(props)))
                output.append(f"\n📦 Entidade: {model}")
                output.append(f"   Colunas prováveis: {props_list}")
        
        if count_models == 0:
            output.append("\n   (Nenhum modelo de dados claro foi detectado)")

        return "\n".join(output)


#================================================================================
# BLOCO 4: APLICAÇÃO PRINCIPAL (UI CORRIGIDA)
#================================================================================

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("ToolKitDev v3 - Suíte de Engenharia")
        self.geometry("950x700")
        self.minsize(800, 600)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # --- Variáveis de estado ---
        self.export_project_path = ctk.StringVar()
        self.export_output_name = ctk.StringVar(value="projeto_para_ia.md")
        self.export_analyzer = None
        self.export_analysis_thread = None
        self.export_profile_vars = {}

        self.create_itens_faltantes = {'pastas': [], 'arquivos': []}
        self.create_project_dir = ctk.StringVar(value=os.getcwd())
        
        # [NOVO] Variável para o Scanner
        self.scanner_project_path = ctk.StringVar()

        # --- Estrutura Principal ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Seletor de Modo ---
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        mode_frame.grid_columnconfigure(0, weight=1)
        
        # [CORREÇÃO] Adicionado "Scanner (Sherlock)" nas opções
        self.mode_switcher = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Exportar Template", "Criar por Template", "Scanner (Sherlock)"],
            command=self._switch_mode
        )
        self.mode_switcher.grid(row=0, column=0, sticky="ew")
        
        # --- Frames (Telas) ---
        self.export_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.export_frame.grid_rowconfigure(2, weight=1)
        self.export_frame.grid_columnconfigure(0, weight=1)

        self.create_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.create_frame.grid_rowconfigure(2, weight=1)
        self.create_frame.grid_columnconfigure(0, weight=1)
        self.create_frame.grid_columnconfigure(1, weight=1)

        # [NOVO] Frame do Scanner
        self.scanner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.scanner_frame.grid_columnconfigure(1, weight=1)
        self.scanner_frame.grid_rowconfigure(2, weight=1)

        # Montar as telas
        self._create_export_widgets(self.export_frame)
        self._create_create_widgets(self.create_frame)
        self._create_scanner_widgets(self.scanner_frame) # [NOVO]
        
        # Inicia no modo "Exportar"
        self.mode_switcher.set("Exportar Template")
        self._switch_mode("Exportar Template")
        
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _switch_mode(self, mode):
        # Esconde todos primeiro
        self.export_frame.grid_forget()
        self.create_frame.grid_forget()
        self.scanner_frame.grid_forget()

        # Mostra o selecionado
        if mode == "Exportar Template":
            self.export_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        elif mode == "Criar por Template":
            self.create_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        elif mode == "Scanner (Sherlock)":
            self.scanner_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    # ============================================================
    #  MÉTODOS TELA 1: EXPORTAR
    # ============================================================
    def _create_export_widgets(self, tab):
        config_frame = ctk.CTkFrame(tab, fg_color="transparent")
        config_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(config_frame, text="Pasta do Projeto:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        ctk.CTkEntry(config_frame, textvariable=self.export_project_path).grid(row=0, column=1, sticky="ew", pady=5)
        ctk.CTkButton(config_frame, text="📁 Buscar", width=100, command=self._export_select_folder).grid(row=0, column=2, padx=(10, 0), pady=5)

        ctk.CTkLabel(config_frame, text="Nome do .md (IA):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        ctk.CTkEntry(config_frame, textvariable=self.export_output_name).grid(row=1, column=1, sticky="ew", pady=5)
        
        profiles_frame = ctk.CTkFrame(tab)
        profiles_frame.grid(row=1, column=0, padx=0, pady=10, sticky="ew")
        ctk.CTkLabel(profiles_frame, text="Perfis para Ignorar:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=10)
        profiles = [('Python', 'python'), ('React/Node.js', 'react'), ('PHP/Laravel', 'php'), ('Spring/Java', 'spring'), ('Node.js', 'node')]
        self.export_profile_vars = {}
        for i, (label, value) in enumerate(profiles):
            var = ctk.BooleanVar()
            self.export_profile_vars[value] = var
            ctk.CTkCheckBox(profiles_frame, text=label, variable=var).grid(row=1, column=i, sticky="w", padx=10, pady=(0, 10))

        log_frame = ctk.CTkFrame(tab)
        log_frame.grid(row=2, column=0, padx=0, pady=(0, 10), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_frame, text="Log de Execução:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        self.export_log_text = ctk.CTkTextbox(log_frame, wrap=tk.WORD, state='disabled')
        self.export_log_text.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        self.export_progress_label = ctk.CTkLabel(log_frame, text="Pronto.")
        self.export_progress_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
        self.export_progress = ctk.CTkProgressBar(log_frame, mode='indeterminate')
        self.export_progress.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.export_progress.set(0)

        button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=0, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        self.export_start_btn = ctk.CTkButton(button_frame, text="▶️ Iniciar Exportação (Gera .txt e .md)", command=self._export_start_analysis, height=35)
        self.export_start_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.export_cancel_btn = ctk.CTkButton(button_frame, text="⏹️ Cancelar", command=self._export_cancel_analysis, state='disabled', fg_color="tomato", hover_color="darkred", height=35)
        self.export_cancel_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _export_log(self, message: str):
        self.export_log_text.configure(state='normal')
        self.export_log_text.insert(tk.END, f"{message}\n")
        self.export_log_text.see(tk.END)
        self.export_log_text.configure(state='disabled')
    
    def _export_select_folder(self):
        try:
            folder = filedialog.askdirectory(title="Selecione a pasta do projeto", mustexist=True)
            if folder:
                self.export_project_path.set(folder)
                self._export_log(f"✅ Pasta selecionada: {folder}")
        except Exception as e:
            self._export_log(f"❌ Erro ao selecionar pasta: {e}")

    def _export_validate_inputs(self) -> bool:
        if not self.export_project_path.get():
            messagebox.showerror("Erro", "Selecione uma pasta do projeto!")
            return False
        if not os.path.isdir(self.export_project_path.get()):
            messagebox.showerror("Erro", "A pasta selecionada não existe!")
            return False
        if not self.export_output_name.get():
            messagebox.showerror("Erro", "Digite um nome para o arquivo de saída .md!")
            return False
        return True
    
    def _export_start_analysis(self):
        if not self._export_validate_inputs():
            return
        
        self.export_start_btn.configure(state='disabled')
        self.export_cancel_btn.configure(state='normal')
        self.export_log_text.configure(state='normal')
        self.export_log_text.delete('1.0', tk.END)
        self.export_log_text.configure(state='disabled')
        self.export_progress.start()
        self.export_progress.set(1)
        self.export_progress_label.configure(text="⏳ Analisando projeto...")
        
        selected_profiles = [key for key, var in self.export_profile_vars.items() if var.get()]
        
        self.export_analysis_thread = threading.Thread(
            target=self._export_run_analysis,
            args=(self.export_project_path.get(), self.export_output_name.get(), selected_profiles),
            daemon=True
        )
        self.export_analysis_thread.start()
        self._export_check_thread()
    
    def _export_run_analysis(self, project_path: str, output_name_md: str, profiles: list):
        try:
            self.export_analyzer = ProjectAnalyzer(project_path, output_name_md)
            self.export_analyzer.set_profiles(profiles)
            
            old_stdout = sys.stdout
            redirected_output = io.StringIO()
            sys.stdout = redirected_output
            
            print("📂 Gerando árvore de template...")
            tree_content = self.export_analyzer._generate_tree()
            
            project_name = Path(project_path).name
            template_filename = f"{project_name}_template.txt"
            
            output_dir = os.path.dirname(output_name_md)
            if not output_dir: output_dir = os.getcwd()
            
            template_filepath = os.path.join(output_dir, template_filename)
            
            try:
                with open(template_filepath, 'w', encoding='utf-8') as f:
                    f.write(tree_content)
                print(f"✅ Template salvo com sucesso em: {template_filepath}")
            except Exception as e:
                print(f"❌ Erro ao salvar template .txt: {e}")
            
            success = self.export_analyzer.generate_report(tree_content)
            
            output = redirected_output.getvalue()
            sys.stdout = old_stdout
            
            self.after(0, self._export_analysis_complete, success, output, template_filepath)
            
        except Exception as e:
            error_msg = f"Erro crítico: {e}\n{traceback.format_exc()}"
            sys.stdout = old_stdout
            self.after(0, self._export_analysis_error, error_msg)
    
    def _export_check_thread(self):
        if self.export_analysis_thread and self.export_analysis_thread.is_alive():
            self.after(100, self._export_check_thread)
        else:
            self.export_progress.stop()
            self.export_progress.set(0)
    
    def _export_analysis_complete(self, success: bool, output: str, template_filepath: str):
        self.export_progress.stop()
        self.export_progress.set(0)
        self.export_start_btn.configure(state='normal')
        self.export_cancel_btn.configure(state='disabled')
        
        for line in output.split('\n'):
            if line.strip(): self._export_log(line)
        
        if success:
            self.export_progress_label.configure(text="✅ Exportação concluída!")
            messagebox.showinfo("Sucesso", f"Exportação concluída!\n\nTemplate: {template_filepath}\nRelatório: {self.export_output_name.get()}")
        else:
            self.export_progress_label.configure(text="❌ Erro na exportação")
            messagebox.showwarning("Aviso", "Concluído com erros. Verifique o log.")
    
    def _export_analysis_error(self, error_msg: str):
        self.export_progress.stop()
        self.export_progress.set(0)
        self.export_start_btn.configure(state='normal')
        self.export_cancel_btn.configure(state='disabled')
        self.export_progress_label.configure(text="❌ Erro crítico")
        self._export_log(f"\n❌ ERRO CRÍTICO:\n{error_msg}")
        messagebox.showerror("Erro", error_msg[:200])
    
    def _export_cancel_analysis(self):
        if self.export_analyzer:
            self.export_analyzer.cancelled = True
            self._export_log("⏹️ Cancelamento solicitado...")
            self.export_progress_label.configure(text="⏹️ Cancelando...")

    # ============================================================
    #  MÉTODOS TELA 2: CRIAR
    # ============================================================
    def _create_create_widgets(self, tab):
        left_frame = ctk.CTkFrame(tab, fg_color="transparent")
        left_frame.grid(row=0, column=0, rowspan=4, padx=(0, 10), pady=0, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_frame, text="Estrutura do Template", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        self.create_structure_area = ctk.CTkTextbox(left_frame, wrap=tk.WORD, font=('Courier New', 12))
        self.create_structure_area.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.create_structure_area.insert(tk.END, "# Cole sua estrutura aqui ou carregue um arquivo...")

        ctk.CTkButton(left_frame, text="Carregar Template (.txt)...", command=self._create_carregar_estrutura).grid(row=2, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(left_frame, text="Salvar...", command=self._create_exportar_estrutura).grid(row=2, column=1, sticky="ew", padx=(5, 0))

        right_frame = ctk.CTkFrame(tab, fg_color="transparent")
        right_frame.grid(row=0, column=1, rowspan=4, padx=(10, 0), pady=0, sticky="nsew")
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_frame, text="Pasta Base do Novo Projeto", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        
        path_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        path_frame.grid_columnconfigure(0, weight=1)
        
        self.create_path_entry = ctk.CTkEntry(path_frame, textvariable=self.create_project_dir)
        self.create_path_entry.grid(row=0, column=0, sticky="ew")
        self.create_path_entry.configure(state="readonly")
        ctk.CTkButton(path_frame, text="Selecionar Destino...", width=140, command=self._create_selecionar_pasta_projeto).grid(row=0, column=1, sticky="e", padx=(10,0))
        
        self.create_log_area = ctk.CTkTextbox(right_frame, wrap=tk.WORD, font=('Courier New', 12))
        self.create_log_area.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        self.create_log_area.configure(state=tk.DISABLED)

        self.create_verify_button = ctk.CTkButton(right_frame, text="Verificar Estrutura", command=self._create_verificar_estrutura, height=35)
        self.create_verify_button.grid(row=3, column=0, sticky="ew", padx=(0, 5))

        self.create_create_button = ctk.CTkButton(right_frame, text="Criar Itens Faltantes", command=self._create_criar_estrutura, state=tk.DISABLED, height=35)
        self.create_create_button.grid(row=3, column=1, sticky="ew", padx=(5, 0))

        self.create_status_label = ctk.CTkLabel(right_frame, text="Pronto.", anchor='w', height=25)
        self.create_status_label.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self._create_verificar_estrutura()

    def _create_log(self, message):
        self.create_log_area.configure(state=tk.NORMAL)
        self.create_log_area.insert(tk.END, message + "\n")
        self.create_log_area.configure(state=tk.DISABLED)
        self.create_log_area.see(tk.END)

    def _create_selecionar_pasta_projeto(self):
        diretorio = filedialog.askdirectory(title="Selecione a pasta raiz", initialdir=self.create_project_dir.get())
        if diretorio:
            self.create_project_dir.set(diretorio)
            self.create_path_entry.configure(state="normal")
            self.create_path_entry.delete(0, tk.END)
            self.create_path_entry.insert(0, diretorio)
            self.create_path_entry.configure(state="readonly")
            self.create_status_label.configure(text=f"Pasta selecionada.")
            self._create_verificar_estrutura()

    def _create_carregar_estrutura(self):
        filepath = filedialog.askopenfilename(title="Selecione um template", filetypes=[("Texto", "*.txt"), ("Markdown", "*.md"), ("Todos", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.create_structure_area.delete('1.0', tk.END)
                    self.create_structure_area.insert('1.0', f.read())
                self.create_status_label.configure(text=f"Template carregado.")
                self._create_verificar_estrutura()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler arquivo:\n{e}")

    def _create_exportar_estrutura(self):
        filepath = filedialog.asksaveasfilename(title="Salvar estrutura", defaultextension=".txt")
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.create_structure_area.get('1.0', tk.END))
                messagebox.showinfo("Sucesso", f"Salvo em:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar:\n{e}")

    def _create_get_base_dir_and_structure(self):
        estrutura_atual = self.create_structure_area.get('1.0', tk.END)
        estrutura = extrair_estrutura(estrutura_atual)
        pastas_esperadas = estrutura['pastas']
        current_project_dir = self.create_project_dir.get()
        
        if not pastas_esperadas:
            return current_project_dir, {'pastas': [], 'arquivos': []}

        raiz_estrutura = pastas_esperadas[0].split(os.sep)[0]
        base_selecionada = os.path.basename(os.path.normpath(current_project_dir))
        diretorio_base = current_project_dir
        
        if raiz_estrutura and raiz_estrutura == base_selecionada:
            diretorio_base = os.path.dirname(current_project_dir)
            
        return diretorio_base, estrutura

    def _create_verificar_estrutura(self):
        self.create_log_area.configure(state=tk.NORMAL)
        self.create_log_area.delete('1.0', tk.END)
        self.create_log_area.configure(state=tk.DISABLED)
        
        self.create_itens_faltantes = {'pastas': [], 'arquivos': []}
        self.create_create_button.configure(state=tk.DISABLED)
        self.create_status_label.configure(text="Verificando...")

        diretorio_base, estrutura = self._create_get_base_dir_and_structure()
        pastas_esperadas = estrutura['pastas']
        arquivos_esperados = estrutura['arquivos']

        if not pastas_esperadas and not arquivos_esperados:
            self._create_log("Estrutura vazia.")
            self.create_status_label.configure(text="Estrutura vazia.")
            return

        self._create_log(f"--- BASE: {diretorio_base} ---")
        
        for pasta in pastas_esperadas:
            path = os.path.join(diretorio_base, pasta)
            if os.path.isdir(path): self._create_log(f"[OK] (Pasta) {pasta}")
            else:
                self._create_log(f"[FALTANDO] (Pasta) {pasta}")
                self.create_itens_faltantes['pastas'].append(pasta)
        
        for arquivo in arquivos_esperados:
            path = os.path.join(diretorio_base, arquivo)
            if os.path.isfile(path): self._create_log(f"[OK] (Arquivo) {arquivo}")
            else:
                self._create_log(f"[FALTANDO] (Arquivo) {arquivo}")
                self.create_itens_faltantes['arquivos'].append(arquivo)
        
        total = len(self.create_itens_faltantes['pastas']) + len(self.create_itens_faltantes['arquivos'])
        if total == 0:
            self._create_log("\n✅ Estrutura completa!")
            self.create_status_label.configure(text="Tudo ok.")
        else:
            self._create_log(f"\n⚠️ {total} itens faltando.")
            self.create_status_label.configure(text=f"{total} faltando.")
            self.create_create_button.configure(state=tk.NORMAL)

    def _create_criar_estrutura(self):
        total = len(self.create_itens_faltantes['pastas']) + len(self.create_itens_faltantes['arquivos'])
        if total == 0: return

        diretorio_base, _ = self._create_get_base_dir_and_structure()
        if not messagebox.askyesno("Criar", f"Criar {total} itens em:\n{diretorio_base}?"): return

        self._create_log("\n--- CRIANDO ---")
        criados = 0
        
        for pasta in self.create_itens_faltantes['pastas']:
            p = os.path.join(diretorio_base, pasta)
            try:
                os.makedirs(p, exist_ok=True)
                self._create_log(f"[CRIADA] {pasta}")
                criados += 1
            except OSError as e: self._create_log(f"[ERRO] {pasta}: {e}")

        for arquivo in self.create_itens_faltantes['arquivos']:
            p = os.path.join(diretorio_base, arquivo)
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, 'w') as f: pass
                self._create_log(f"[CRIADO] {arquivo}")
                criados += 1
            except OSError as e: self._create_log(f"[ERRO] {arquivo}: {e}")

        self._create_log("\n✨ Concluído!")
        self.create_status_label.configure(text=f"{criados} criados.")
        self.create_create_button.configure(state=tk.DISABLED)
        self._create_verificar_estrutura()

    # ============================================================
    #  MÉTODOS TELA 3: SCANNER (SHERLOCK)
    # ============================================================
    def _create_scanner_widgets(self, frame):
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="Analise a pasta 'src' do Frontend para descobrir rotas e modelos.", 
                     text_color="gray").grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 20))

        ctk.CTkLabel(frame, text="Pasta 'src':").grid(row=1, column=0, padx=10, sticky="w")
        ctk.CTkEntry(frame, textvariable=self.scanner_project_path).grid(row=1, column=1, padx=10, sticky="ew")
        ctk.CTkButton(frame, text="📁 Buscar", width=80, command=self._sel_scanner_folder).grid(row=1, column=2, padx=10)

        self.txt_scanner_result = ctk.CTkTextbox(frame, font=("Courier New", 13), fg_color="#1e1e1e", text_color="#00ff00")
        self.txt_scanner_result.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.txt_scanner_result.insert("0.0", ">>> Aguardando ordem de análise...\n")

        self.btn_scan = ctk.CTkButton(frame, text="🕵️ Executar Análise Sherlock", 
                                      command=self._run_scanner, height=40, fg_color="#D4AF37", text_color="#001B3D")
        self.btn_scan.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    def _sel_scanner_folder(self):
        f = filedialog.askdirectory(title="Selecione a pasta src do frontend")
        if f: self.scanner_project_path.set(f)

    def _run_scanner(self):
        path = self.scanner_project_path.get()
        if not path or not os.path.exists(path):
            messagebox.showerror("Erro", "Selecione uma pasta válida")
            return
        
        self.txt_scanner_result.delete("1.0", "end")
        self.txt_scanner_result.insert("end", f"⏳ Iniciando análise em: {path}...\n\n")
        self.update()

        scanner = FrontendScanner(path)
        report = scanner.scan()
        
        self.txt_scanner_result.delete("1.0", "end")
        self.txt_scanner_result.insert("end", report)

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar a aplicação: {e}")
        print(traceback.format_exc())
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Fatal", f"Ocorreu um erro crítico ao iniciar:\n\n{e}\n\nVeja o console para detalhes.")
            root.destroy()
        except Exception:
            pass
        sys.exit(1)