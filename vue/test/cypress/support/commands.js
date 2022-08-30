// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
import 'cypress-file-upload';

Cypress.Commands.add('cleardb', () =>{
  indexedDB.deleteDatabase("faodb")
})

Cypress.Commands.add('login', (user) => {
  cy.visit('/login')
  cy.contains('.subtitle-2', 'Sector Agropecuario').should('be.visible')
  cy.get('#input-14').type(user.email)
  cy.get('#input-32').type(user.password)
  cy.get('.background-primary').click()
})

Cypress.Commands.add('logout', () => {
  cy.get(':nth-child(11) > .hidden-sm-and-down').click()
  cy.contains('Cerrar cesión').click()
})