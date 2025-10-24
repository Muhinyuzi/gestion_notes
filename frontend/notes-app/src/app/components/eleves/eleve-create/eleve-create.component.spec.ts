import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EleveCreateComponent } from './eleve-create.component';

describe('EleveCreateComponent', () => {
  let component: EleveCreateComponent;
  let fixture: ComponentFixture<EleveCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EleveCreateComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EleveCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
