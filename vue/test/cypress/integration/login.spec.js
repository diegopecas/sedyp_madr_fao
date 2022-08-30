import { clearIndexedDb } from './common';

describe('Pruebas de login', () => {
  before(() => {
    clearIndexedDb();
    cy.fixture('user.json').as('user')
  })


  it('Login éxitoso', () => {
    cy.get('@user').then(user => {
      cy.login(user)
      cy.wait(5000)
      cy.contains('h3', 'LISTADO EVENTOS').should('be.visible')
      cy.logout()
    })
  })

  it('login fallido', () => {
    cy.login({email: 'email@email.com', password: '123456'})
    cy.contains('#swal2-content', 'Usuario no encontrado').should('be.visible')
  })

})