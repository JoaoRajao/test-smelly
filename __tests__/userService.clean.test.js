const { UserService } = require('../src/userService');

describe('UserService - testes de comportamento', () => {
  let userService;

  beforeEach(() => {
    userService = new UserService();
    userService._clearDB();
  });

  test('cria um usuário com os dados fornecidos e status ativo', () => {
    // Arrange
    const dados = { nome: 'Alice', email: 'alice@email.com', idade: 28 };

    // Act
    const usuario = userService.createUser(dados.nome, dados.email, dados.idade);

    // Assert
    expect(usuario).toEqual(expect.objectContaining({ ...dados, status: 'ativo' }));
    expect(usuario.id).toEqual(expect.any(String));
  });

  test('busca pelo identificador um usuário previamente cadastrado', () => {
    // Arrange
    const usuario = userService.createUser('Alice', 'alice@email.com', 28);

    // Act
    const encontrado = userService.getUserById(usuario.id);

    // Assert
    expect(encontrado).toEqual(expect.objectContaining({
      id: usuario.id,
      nome: 'Alice',
      email: 'alice@email.com',
    }));
  });

  test('retorna null ao buscar um identificador inexistente', () => {
    // Arrange
    const idInexistente = 'id-inexistente';

    // Act
    const encontrado = userService.getUserById(idInexistente);

    // Assert
    expect(encontrado).toBeNull();
  });

  test('desativa um usuário comum', () => {
    // Arrange
    const usuario = userService.createUser('Comum', 'comum@teste.com', 30);

    // Act
    const desativou = userService.deactivateUser(usuario.id);

    // Assert
    expect(desativou).toBe(true);
    expect(userService.getUserById(usuario.id)).toEqual(expect.objectContaining({ status: 'inativo' }));
  });

  test('mantém ativo um administrador quando a desativação é solicitada', () => {
    // Arrange
    const administrador = userService.createUser('Admin', 'admin@teste.com', 40, true);

    // Act
    const desativou = userService.deactivateUser(administrador.id);

    // Assert
    expect(desativou).toBe(false);
    expect(userService.getUserById(administrador.id)).toEqual(expect.objectContaining({ status: 'ativo' }));
  });

  test('retorna false ao tentar desativar um usuário inexistente', () => {
    // Arrange
    const idInexistente = 'id-inexistente';

    // Act
    const desativou = userService.deactivateUser(idInexistente);

    // Assert
    expect(desativou).toBe(false);
  });

  test('inclui os usuários cadastrados no relatório', () => {
    // Arrange
    userService.createUser('Alice', 'alice@email.com', 28);
    userService.createUser('Bob', 'bob@email.com', 32);

    // Act
    const relatorio = userService.generateUserReport();

    // Assert
    expect(relatorio).toContain('Nome: Alice');
    expect(relatorio).toContain('Nome: Bob');
    expect(relatorio).toContain('Status: ativo');
  });

  test('informa quando o relatório não tem usuários', () => {
    // Arrange: o banco é limpo no beforeEach.

    // Act
    const relatorio = userService.generateUserReport();

    // Assert
    expect(relatorio).toContain('Nenhum usuário cadastrado.');
  });

  test('rejeita o cadastro de menores de idade', () => {
    // Arrange
    const cadastrarMenor = () => userService.createUser('Menor', 'menor@email.com', 17);

    // Act e Assert: a chamada ocorre dentro do matcher, que exige a exceção.
    expect(cadastrarMenor).toThrow('O usuário deve ser maior de idade.');
  });
});
