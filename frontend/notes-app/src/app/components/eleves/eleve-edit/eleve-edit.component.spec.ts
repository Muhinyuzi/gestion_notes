import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EleveEditComponent } from './eleve-edit.component';

describe('EleveEditComponent', () => {
  let component: EleveEditComponent;
  let fixture: ComponentFixture<EleveEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EleveEditComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EleveEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
