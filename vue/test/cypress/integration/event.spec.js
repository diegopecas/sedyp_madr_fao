describe('Test de eventos', () => {
  before(() => {
    cy.fixture('user.json').as('user')
    cy.fixture('event.json').as('event')
    cy.get('@user').then ((user) => {
      cy.login(user)
    })
    // Click new event tab
    cy.get('.v-toolbar__items > :nth-child(2)').click()
  })

  it('Registrando evento agrícola', () => {
    
    
    cy.get('@event').then((event) => {
      
      // Producer info
      cy.get('.background-primary').click()
      cy.get(':nth-child(3) > .v-form > .row > :nth-child(1) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.cond)
      cy.get(':nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.name)
      cy.get(':nth-child(3) > .v-form > .row > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.typeDoc)
      cy.get(':nth-child(3) > .v-form > .row > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.doc)
      cy.get(':nth-child(3) > .v-form > .row > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.email)
      cy.get(':nth-child(6) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.typeProd)
      cy.get(':nth-child(3) > .v-form > .row > :nth-child(7) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.estate)
      cy.get(':nth-child(8) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.addr)
      cy.get(':nth-child(9) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.tel)
      cy.get(':nth-child(10) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.sex)
      cy.get(':nth-child(12) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').click()
      cy.get(':nth-child(4) > :nth-child(2) > .v-btn').click()
      cy.get(':nth-child(13) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.et)
      cy.get('.col-md-12 > .v-input > .v-input__control > .v-input__slot > .v-input--selection-controls__input > .v-input--selection-controls__ripple').click()
      cy.get('.col-md-2 > .background-primary').click()
      
      // Location info
      //cy.get('.color-primary-dark > .v-btn__content > .v-icon').click()
      cy.get('.v-stepper__header > :nth-child(3)').click()
      cy.fixture('crop.jpg').then(fileContent => {
        cy.get('.v-file-input__text').attachFile({
          fileContent: fileContent.toString(),
          fileName: 'crop.jpg',
          mimeType: 'image/jpg'
        })
      })
      cy.get('.section > .v-form > .row > :nth-child(5) > .v-input > .v-input__control > .v-input__slot').type(event.location.pres)
      cy.get('.section > .v-form > .row > .col-md-12 > .v-input > .v-input__control > .v-input__slot').type(event.location.alt)
      cy.get('.section > .v-form > .row > :nth-child(7) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.location.dpto)
      cy.get(':nth-child(8) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.location.mun)
      cy.get(':nth-child(10) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.location.obs)
      cy.get('.col-md-3 > .background-primary-dark').click()
      cy.get('.swal2-confirm').click()
      
      // Event info
      cy.get('.v-stepper__step--inactive').click()
      cy.get('.v-stepper__wrapper > .container > .v-form > .row > :nth-child(1) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.typeEv)
      cy.get(':nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.typeSubEv)
      cy.get('.v-stepper__wrapper > .container > .v-form > .row > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.cuarent)
      cy.get(':nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.plag)
      cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections').type(event.event.exp)
      
      cy.get('.v-toolbar__content > .background-primary-dark').click()
      cy.get(':nth-child(2) > :nth-child(1) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.cropName)
      cy.get(':nth-child(2) > :nth-child(1) > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.reportUnit)
      cy.get(':nth-child(2) > :nth-child(1) > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.areaCrop)
      cy.get(':nth-child(2) > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.material)
      cy.get(':nth-child(2) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.amount)
      cy.get(':nth-child(2) > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.reportUnit1)
      cy.get(':nth-child(2) > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.sourceSeed)
      cy.get(':nth-child(3) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').click()
      cy.get('.menuable__content__active > .col-md-4 > .v-picker > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(4) > :nth-child(6) > .v-btn > .v-btn__content').click()
      cy.get(':nth-child(3) > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').click()
      cy.get('.menuable__content__active > .col-md-4 > .v-picker > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(4) > :nth-child(1) > .v-btn').click()
      cy.get(':nth-child(4) > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.produced)
      cy.get(':nth-child(4) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.reportUnit1)
      cy.get(':nth-child(4) > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.totalPrice)
      cy.get(':nth-child(5) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').click()
      cy.get('.menuable__content__active > .col-md-4 > .v-picker > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(4) > :nth-child(6) > .v-btn').click()
      cy.get(':nth-child(5) > .col-sm-6 > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.daysExposed)
      cy.get(':nth-child(6) > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.amount)
      cy.get(':nth-child(6) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.reportUnit1)
      cy.get(':nth-child(6) > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get(':nth-child(6) > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.totalPrice)
      cy.get(':nth-child(4) > .row > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get(':nth-child(4) > .row > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.act1)
      //cy.get(':nth-child(4) > .row > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.numJorn)
      //cy.get(':nth-child(4) > .row > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get(':nth-child(4) > .row > .col-md-3 > .background-primary-dark').click()
      //cy.get(':nth-child(4) > .row > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get(':nth-child(4) > .row > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.act2)
      //cy.get(':nth-child(4) > .row > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.numJorn)
      cy.get(':nth-child(4) > .row > .col-md-3 > .background-primary-dark').click()
      cy.get(':nth-child(5) > .row > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.act3)
      cy.get(':nth-child(5) > .row > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get(':nth-child(5) > .row > .col-md-3 > .background-primary-dark').click()
      cy.get(':nth-child(5) > .row > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.act4)
      cy.get(':nth-child(5) > .row > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get(':nth-child(5) > .row > .col-md-3 > .background-primary-dark').click()

      cy.get('.ml-1 > .v-input > .v-input__control > .v-input__slot > .v-input--selection-controls__input > .v-input--selection-controls__ripple').click()
      cy.get(':nth-child(6) > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.material)
      cy.get('.container > :nth-child(1) > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.cropName)
      cy.get('.container > :nth-child(1) > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.amount)
      cy.get('.container > :nth-child(1) > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.kgPrice)
      cy.get('.v-form > .container > .mt-5 > :nth-child(2) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.material)
      cy.get('.container > .mt-5 > :nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot').type(event.event.agro.amount)
      cy.get('.container > .mt-5 > :nth-child(4) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.reportUnit1)
      cy.get('.container > .mt-5 > :nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').type(event.event.agro.sourceSeed)
      cy.get('.v-card__actions > :nth-child(3)').click()
      cy.get(':nth-child(7) > .col-md-3 > .success').click()
      cy.get(':nth-child(3) > .col-md-3 > .success').click()
      cy.wait(35000)
      cy.get('.swal2-confirm').should('be.visible')
      cy.get('.swal2-confirm').click()
    })
    
    cy.logout()
  })
})