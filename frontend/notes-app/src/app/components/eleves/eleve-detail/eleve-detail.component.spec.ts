import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EleveDetailComponent } from './eleve-detail.component';

describe('EleveDetailComponent', () => {
  let component: EleveDetailComponent;
  let fixture: ComponentFixture<EleveDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EleveDetailComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EleveDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
